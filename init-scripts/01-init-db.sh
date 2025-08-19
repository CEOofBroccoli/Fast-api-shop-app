#!/bin/bash
set -e

# This script is run when the Postgres container is created for the first time
# It sets up initial database security and configuration

# Enhanced security settings
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  -- Set password encryption to scram-sha-256 (more secure than md5)
  ALTER SYSTEM SET password_encryption = 'scram-sha-256';
  
  -- Limit failed login attempts
  ALTER SYSTEM SET authentication_timeout = '30s';
  
  -- Disable SSL for now (no certificates available)
  ALTER SYSTEM SET ssl = off;
  
  -- Audit logging
  ALTER SYSTEM SET log_connections = on;
  ALTER SYSTEM SET log_disconnections = on;
  ALTER SYSTEM SET log_statement = 'ddl';
  
  -- Connection settings
  ALTER SYSTEM SET max_connections = 100;
  ALTER SYSTEM SET idle_in_transaction_session_timeout = '60s';
  ALTER SYSTEM SET statement_timeout = '30s';
  
  -- Reload config
  SELECT pg_reload_conf();
  
  -- Create application roles with least privilege
  CREATE ROLE app_read WITH LOGIN PASSWORD '${APP_READ_PASSWORD:-readuser}' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
  CREATE ROLE app_write WITH LOGIN PASSWORD '${APP_WRITE_PASSWORD:-writeuser}' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
  
  -- Grant appropriate permissions
  GRANT CONNECT ON DATABASE $POSTGRES_DB TO app_read;
  GRANT CONNECT ON DATABASE $POSTGRES_DB TO app_write;
EOSQL

# Create schema objects and permissions after database is created
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  -- Schema permissions setup
  CREATE SCHEMA IF NOT EXISTS app;
  
  -- Grant permissions on schema level
  GRANT USAGE ON SCHEMA app TO app_read;
  GRANT USAGE, CREATE ON SCHEMA app TO app_write;
  
  -- Set default permissions for future objects
  ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES TO app_read;
  ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_write;
  ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT USAGE ON SEQUENCES TO app_read;
  ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO app_write;
  
  -- Create admin user for application if specified in env vars
  DO \$\$
  BEGIN
    IF '${ADMIN_USERNAME}' != '' AND '${ADMIN_PASSWORD}' != '' THEN
      CREATE EXTENSION IF NOT EXISTS pgcrypto;
      INSERT INTO app.users (username, email, password_hash, role, is_active, is_verified)
      VALUES ('${ADMIN_USERNAME}', '${ADMIN_EMAIL:-admin@example.com}', 
              crypt('${ADMIN_PASSWORD}', gen_salt('bf')), 'admin', true, true)
      ON CONFLICT (username) DO NOTHING;
    END IF;
  EXCEPTION
    WHEN undefined_table THEN
      RAISE NOTICE 'Users table does not exist yet, admin user will be created via application setup';
  END;
  \$\$;
EOSQL

echo "Database initialization completed successfully!"
