### Med Sandbox - posts on interesting medical topics

### Authenticated users can create a comment

### Banned or Unauthenticated users can only read content

1. django 4.2

2. auth (allauth)

3. Unit tests

4. Images upload: aws s3

5. Notifications

6. Nested comments

7. Static and dynamic translations

8. newsletter (celery + redis or cron)

9. django templates + htmx

## notifications flow

```
1. admin can ban users (via admin based on django signals creating new object notification)
2. ban has start_ban and end_ban
3. unban:
  2.1 auto unban via cropjob (management command unban.py)
  2.2 via admin panel (manually by admin)
3. notifications about (reply) comments: UI menu panel dropdown
  last five replies, if more - button triggering htmx request to fetch the rest
4. user can clean notification dropdown via option "mark-read"

```

## setup

```
1. python -m venv venv
2. Linux:   pip install -r reqs/dev.txt -r reqs/req_linux.txt
2. Windows: pip install -r reqs/dev.txt -r reqs/req.txt

```

## site live

`https://medsandbox.nl/en/posts/`
