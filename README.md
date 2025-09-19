# Expenses Tracker API

## Deployment with Nginx & Let's Encrypt

### Setup

1. Configure `.env.prod` with domain, email, and database settings.
2. Obtain certificates (first time only):
   ```bash
   docker compose run --rm certbot
   ```
3. Start services:
    ```bash
    docker compose up -d api postgres migrations nginx certbot-renew
    ```

## Notes

- nginx serves HTTPS using certificates from certbot
- certbot-renew runs in background and reloads nginx when certs are renewed.
- All HTTP traffic redirected to HTTPS