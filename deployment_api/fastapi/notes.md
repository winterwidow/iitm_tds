# 1. FastAPI

FastAPI is used when you want to turn ``Python`` code into an ``HTTP API``.

![FastAPI image](image.png)

A small CRUD API uses the following pattern repeatedly:
## 1. routes
FASTAPI routes are made using decorators. A decorator connects an HTTP method and URL path to a Python function.

Think of HTTP methods like this:

```
GET     read data
POST    create or submit data
PUT     replace full object
PATCH   update part of object
DELETE  remove object
```

