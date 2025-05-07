# PostgreSQL User and Database Setup for Orderservice Tests

The following SQL commands need to be run manually in your PostgreSQL environment to create the user and test database required for running the Orderservice tests.

## Steps

1. Open a terminal and connect to PostgreSQL as a superuser (e.g., `postgres`):

```bash
sudo -u postgres psql
```

or if you have a password for the superuser:

```bash
psql -U postgres -W
```

2. Run the following SQL commands inside the psql prompt:

```sql
-- Create user if it does not exist
DO
\$\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'orderservice_user'
   ) THEN
      CREATE ROLE orderservice_user LOGIN PASSWORD 'orderservice_pass';
   END IF;
END
\$\$;

-- Create database if it does not exist
DO
\$\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = 'orderservice_test_db'
   ) THEN
      CREATE DATABASE orderservice_test_db OWNER orderservice_user;
   END IF;
END
\$\$;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE orderservice_test_db TO orderservice_user;
```

3. Exit the psql prompt:

```sql
\q
```

4. Rerun your tests.

If you encounter any issues, please ensure your PostgreSQL superuser has the correct permissions and authentication method to run these commands.
