from typing import TYPE_CHECKING, Any

import orjson
import structlog
from boto3 import client as boto3_client
from botocore.client import Config
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
else:
    S3Client = Any

from expenses_tracker.application.interfaces.avatar_storage import IAvatarStorage
from expenses_tracker.core.settings import get_settings

logger = structlog.getLogger(__name__)


class MinioAvatarStorage(IAvatarStorage):
    def __init__(self) -> None:
        self._bucket_name = get_settings().minio_avatar_bucket
        self._internal_client: S3Client | None = None
        self._public_client: S3Client | None = None

        self._ensure_bucket()
        logger.info("MinIO storage initialized", bucket=self._bucket_name)

    @property
    def internal_client(self) -> S3Client:
        if self._internal_client is None:
            self._internal_client = self._create_client(
                get_settings().minio_internal_endpoint
            )
        return self._internal_client

    @property
    def public_client(self) -> S3Client:
        if self._public_client is None:
            self._public_client = self._create_client(
                get_settings().minio_public_endpoint
            )
        return self._public_client

    @staticmethod
    def _create_client(endpoint_url: str) -> S3Client:
        return boto3_client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=get_settings().minio_root_user,
            aws_secret_access_key=get_settings().minio_root_password,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1",
        )

    def _ensure_bucket(self) -> None:
        try:
            self.internal_client.head_bucket(Bucket=self._bucket_name)
            logger.bind(bucket=self._bucket_name).info("Bucket exists")
            self._set_bucket_policy()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                try:
                    self.internal_client.create_bucket(Bucket=self._bucket_name)
                    logger.bind(bucket=self._bucket_name).info("Bucket created")
                    self._set_bucket_policy()
                except ClientError as e2:
                    logger.bind(e2=e2).error("Failed to create bucket")
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
            self.internal_client.put_bucket_policy(
                Bucket=self._bucket_name,
                Policy=orjson.dumps(policy).decode("utf-8"),
            )
            logger.bind(bucket=self._bucket_name).info("Public read policy set")
        except ClientError as e:
            logger.bind(e=e).warning("Could not set bucket policy")

    def get_public_url(self, object_name: str) -> str:
        return (
            f"{get_settings().minio_public_endpoint}/{self._bucket_name}/{object_name}"
        )

    def generate_upload_url(self, object_name: str, expires_in: int = 3600) -> str:
        return self.public_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket_name,
                "Key": object_name,
                "ContentType": self._get_content_type(object_name),
            },
            ExpiresIn=expires_in,
        )

    def object_exists(self, object_name: str) -> bool:
        try:
            self.internal_client.head_object(Bucket=self._bucket_name, Key=object_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                return False
            raise e

    def delete_object(self, object_name: str) -> bool:
        try:
            self.internal_client.delete_object(
                Bucket=self._bucket_name, Key=object_name
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

    def _get_content_type(self, object_name: str) -> str:
        extension = object_name.lower().split(".")[-1]
        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        return content_types.get(extension, "application/octet-stream")

    def close(self) -> None:
        if self._internal_client:
            self._internal_client.close()
        if self._public_client:
            self._public_client.close()
        logger.info("MinIO clients closed")
