# Epic Free Push
automatic Email notification for epic free games.

## quick start
>Python 3.x must be installed.
```sh
git clone git@github.com:yunyuyuan/epic-free-push.git
cd epic-free-push
pip install -r requirement.txt
```
Run every day:
```sh
crontab -e
```
```sh
0 0 * * * /path/to/python /path/to/epic-free-push/main.py
```