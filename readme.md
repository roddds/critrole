# Critical Role Data

## Setup instructions

### Database setup

```sql
CREATE DATABASE critrole;
CREATE USER critrole WITH PASSWORD 'critrole';
ALTER ROLE critrole SET CLIENT_ENCODING TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE 'critrole' TO 'critrole'
ALTER database 'critrole' OWNER TO 'critrole'
ALTER USER 'critrole' CREATEDB;
```

<img
  src="https://github.com/roddds/critrole/blob/app/static/models.png?raw=true"
  alt="Models relationship diagram"
/>

### Create database and import subtitles

```bash
$ pip install -r requirements.txt
$ ./manage.py migrate
$ ./manage.py import_subtitles --path ./subtitles
```

### Updating subtitles from new episodes

```bash
$ cd subtitles/
$ youtube-dl https://www.youtube.com/playlist\?list\=PL1tiwbzkOjQxD0jjAE7PsWoaCrs0EkBH2 \
    --skip-download \
    --write-sub \
    --sub-lang en
```
