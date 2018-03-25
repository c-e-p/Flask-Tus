# Flask-Tus-Fork
This is a fork of [matthoskins1980's implementation of the tus protocol for flask](https://github.com/matthoskins1980/Flask-Tus).

## Prerequisites (redis)

Currently flask-tus is reliant on a local redis server.  This is used for caching information about
uploads in progress.  It is on the roadmap to remove this dependancy.  You must install the redis python package
for this extension to work.

```
pip install redis
```
