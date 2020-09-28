# Critical Role Data

## Setup instructions

### Download all Campaign 2 subtitles

(takes about an hour)

```bash
youtube-dl https://www.youtube.com/playlist\?list\=PL1tiwbzkOjQxD0jjAE7PsWoaCrs0EkBH2 \
    --skip-download \
    --write-sub \
    --sub-lang en
```

and then move them to the `subtitles/` directory

### Database setup

```sql
CREATE DATABASE critrole;
CREATE USER critrole WITH PASSWORD 'critrole';
ALTER ROLE critrole SET CLIENT_ENCODING TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE 'critrole' TO 'critrole'
ALTER database 'critrole' OWNER TO 'critrole'
ALTER USER 'critrole' CREATEDB;
```
