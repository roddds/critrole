# Critical Role Data

## Database setup

```sql
CREATE DATABASE critrole;
CREATE USER critrole WITH PASSWORD 'critrole';
ALTER ROLE critrole SET CLIENT_ENCODING TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE 'critrole' TO 'critrole'
ALTER database 'critrole' OWNER TO 'critrole'
ALTER USER 'critrole' CREATEDB;
```
