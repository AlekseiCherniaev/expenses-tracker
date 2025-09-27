import orjson
import structlog
from boto3 import client
from botocore.client import Config
from botocore.exceptions import ClientError

from expenses_tracker.application.interfaces.avatar_storage import IAvatarStorage
from expenses_tracker.core.settings import get_settings

logger = structlog.getLogger(__name__)


class MinioAvatarStorage(IAvatarStorage):
    def __init__(self) -> None:
        self._client = client(
            "s3",
            endpoint_url=get_settings().minio_endpoint,
            aws_access_key_id=get_settings().minio_access_key,
            aws_secret_access_key=get_settings().minio_secret_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1",
        )
        self._bucket_name = get_settings().minio_avatar_bucket
        self.ensure_bucket()
        logger.info("MinIO client initialized")

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket_name)
            logger.bind(bucket=self._bucket_name).info("Bucket exists")
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                try:
                    self._client.create_bucket(Bucket=self._bucket_name)
                    logger.bind(bucket=self._bucket_name).info("Bucket created")
                    self._set_bucket_policy()

                except ClientError:
                    logger.bind(e=e).error("Failed to create bucket")
                    raise
            else:
                logger.bind(e=e).error("Error checking bucket")
                raise

    def _set_bucket_policy(self) -> None:
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self._bucket_name}/*",
                }
            ],
        }
        try:
            self._client.put_bucket_policy(
                Bucket=self._bucket_name, Policy=orjson.dumps(policy).decode("utf-8")
            )
            logger.bind(bucket=self._bucket_name).info("Public read policy set")
        except ClientError as e:
            logger.bind(e=e).warning("Could not set bucket policy")

    def get_public_url(self, object_name: str) -> str:
        return f"{get_settings().minio_endpoint}/{self._bucket_name}/{object_name}"

    def generate_upload_url(self, object_name: str, expires_in: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self._bucket_name, "Key": object_name},
            ExpiresIn=expires_in,
        )

    def object_exists(self, object_name: str) -> bool:
        try:
            self._client.head_object(
                Bucket=self._bucket_name,
                Key=object_name,
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                return False
            raise e

    def delete_object(self, object_name: str) -> bool:
        try:
            self._client.delete_object(
                Bucket=self._bucket_name,
                Key=object_name,
            )
            logger.bind(bucket=self._bucket_name, key=object_name).info(
                "Deleted object from MinIO"
            )
            return True
        except ClientError as e:
            logger.bind(error=e, bucket=self._bucket_name, key=object_name).error(
                "Failed to delete object from MinIO"
            )
            return False

    def close(self) -> None:
        self._client.close()
        logger.info("MinIO client closed")
