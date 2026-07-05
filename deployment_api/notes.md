# 1. FastAPI

FastAPI is used when you want to turn ``Python`` code into an ``HTTP API``.

[FastAPI image](C:\Users\naija\iitm\iitm_tds\deployment_api\fastapi\image.png)

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

```
@app.get("/items")
def list_items():
    return {"items": ["laptop", "phone"]}

@app.post("/items")
def create_item():
    return {"message": "item created"}
```

Important status codes:

```
200 OK                 normal success
201 Created            created something
202 Accepted           accepted, processing later
204 No Content         success, no response body
400 Bad Request        client sent wrong request
404 Not Found          item does not exist
422 Validation Error   FastAPI/Pydantic validation failed
500 Server Error       bug or unexpected failure
```

[fastapi_example.py](C:\Users\naija\iitm\iitm_tds\deployment_api\fastapi\fastapi_example.py)

the above file can be tested with curl:

```
# Create task
curl -X POST "http://localhost:8000/tasks" \
  -H "content-type: application/json" \
  -d '{"title":"Revise FastAPI","priority":2}'

# List tasks
curl "http://localhost:8000/tasks"

# Filter tasks
curl "http://localhost:8000/tasks?done=false"

# Mark done
curl -X PATCH "http://localhost:8000/tasks/TASK_ID?done=true"

# Delete task
curl -X DELETE "http://localhost:8000/tasks/TASK_ID"
```

***

# 2. CORS and Middleware

