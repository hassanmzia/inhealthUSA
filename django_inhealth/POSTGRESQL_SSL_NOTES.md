# PostgreSQL SSL Configuration Notes

## Current Configuration

PostgreSQL SSL is **disabled** in the development environment for ease of setup and troubleshooting.

**Configuration File:** `/etc/postgresql/16/main/postgresql.conf`

```
ssl = off
```

## Why SSL is Disabled

During initial setup, we encountered SSL certificate permission issues that prevented PostgreSQL from starting. To prioritize getting the application running and address the main migration issues, SSL was temporarily disabled.

## SSL Certificate Issues Encountered

1. **Permission Denied Errors:**
   - PostgreSQL requires strict permissions on SSL private key files
   - The default certificate at `/etc/ssl/private/ssl-cert-snakeoil.key` had permission issues
   - Multiple attempts to fix permissions with different ownership/permission combinations failed

2. **Group Membership Issues:**
   - Adding `postgres` user to `ssl-cert` group didn't resolve the issue
   - PostgreSQL service couldn't read the certificate even with correct group permissions

## Production Recommendations

**DO NOT** run PostgreSQL without SSL in production environments. SSL encryption is essential for:
- Protecting sensitive healthcare data (HIPAA compliance)
- Encrypting data in transit
- Meeting security best practices

## How to Re-enable SSL for Production

### Option 1: Use Certificate in PostgreSQL Data Directory (Recommended)

1. Copy certificates to PostgreSQL data directory:
   ```bash
   sudo cp /etc/ssl/certs/ssl-cert-snakeoil.pem /var/lib/postgresql/16/main/server.crt
   sudo cp /etc/ssl/private/ssl-cert-snakeoil.key /var/lib/postgresql/16/main/server.key
   sudo chown postgres:postgres /var/lib/postgresql/16/main/server.*
   sudo chmod 600 /var/lib/postgresql/16/main/server.key
   sudo chmod 644 /var/lib/postgresql/16/main/server.crt
   ```

2. Update `/etc/postgresql/16/main/postgresql.conf`:
   ```
   ssl = on
   ssl_cert_file = '/var/lib/postgresql/16/main/server.crt'
   ssl_key_file = '/var/lib/postgresql/16/main/server.key'
   ```

3. Restart PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```

### Option 2: Use Real SSL Certificates (Production Only)

For production, obtain proper SSL certificates from a trusted Certificate Authority (CA):

1. Obtain certificates from Let's Encrypt, DigiCert, or your organization's CA

2. Place certificates in PostgreSQL data directory:
   ```bash
   sudo cp /path/to/your/certificate.crt /var/lib/postgresql/16/main/server.crt
   sudo cp /path/to/your/private.key /var/lib/postgresql/16/main/server.key
   sudo chown postgres:postgres /var/lib/postgresql/16/main/server.*
   sudo chmod 600 /var/lib/postgresql/16/main/server.key
   sudo chmod 644 /var/lib/postgresql/16/main/server.crt
   ```

3. Update configuration and restart as shown in Option 1

## Django Connection Settings

When SSL is enabled on PostgreSQL, you may need to update Django's database settings in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inhealth_db',
        'USER': 'inhealth_user',
        'PASSWORD': 'inhealth_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',  # or 'verify-full' with proper certificates
        },
    }
}
```

## Security Considerations

1. **Self-Signed Certificates:**
   - The `ssl-cert-snakeoil` certificates are self-signed
   - Acceptable for development only
   - **Never** use in production

2. **Certificate Permissions:**
   - Private keys must have restrictive permissions (600 or 640)
   - Only postgres user should have read access
   - Public certificates can be world-readable (644)

3. **HIPAA Compliance:**
   - Healthcare applications must encrypt data in transit
   - SSL/TLS is mandatory for production deployments
   - Regular certificate rotation is required

## Testing SSL Configuration

After enabling SSL, verify it's working:

```bash
# Check PostgreSQL is using SSL
sudo -u postgres psql -c "SHOW ssl;"

# Test connection with SSL
psql "sslmode=require host=localhost dbname=inhealth_db user=inhealth_user"
```

## Rollback to No-SSL (Development Only)

If you need to disable SSL again:

```bash
sudo sed -i 's/^ssl = on/ssl = off/' /etc/postgresql/16/main/postgresql.conf
sudo systemctl restart postgresql
```

## Related Files

- PostgreSQL config: `/etc/postgresql/16/main/postgresql.conf`
- Auth config: `/etc/postgresql/16/main/pg_hba.conf`
- Log file: `/var/log/postgresql/postgresql-16-main.log`
- System certificates: `/etc/ssl/certs/` and `/etc/ssl/private/`
- PostgreSQL data: `/var/lib/postgresql/16/main/`

## References

- [PostgreSQL SSL Support Documentation](https://www.postgresql.org/docs/16/ssl-tcp.html)
- [Django Database SSL Options](https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes)
- [Let's Encrypt - Free SSL Certificates](https://letsencrypt.org/)
