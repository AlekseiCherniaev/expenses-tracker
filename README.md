# Expenses Tracker API

## Deployment with Nginx & Let's Encrypt

### Setup

1. Configure `.env` with domain and email
2. Obtain certificates (first time only):
   ```bash
   docker-compose run --rm -p 80:80 certbot
   ```
3. Start services:
    ```bash
    docker-compose up -d --build api postgres redis migrations nginx certbot-renew
    ```

## Notes

- nginx serves HTTPS using certificates from certbot
- certbot-renew runs in the background and reloads nginx when certs are renewed.
- All HTTP traffic is redirected to HTTPS