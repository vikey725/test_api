import uvicorn
from typing import List
from pydantic import BaseModel, Field
from fastapi import FastAPI, Path, Query, Body, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return {'message': "Hello World"}

@app.get("/hello/{name}/{age}")
async def hello(name, age):
   return {"name": name, "age": age}

@app.get("/hello2")
async def hello2(name:str,age:int):
   return {"name": name, "age":age}

# Validation in path
@app.get("/hello3/{name}")
async def hello(name:str=Path(...,min_length=3,
max_length=10)):
   return {"name": name}

@app.get("/hello4/{name}/{age}")
async def hello(*, name: str=Path(...,min_length=3 ,
max_length=10), \
      age: int = Path(..., ge=1, le=100), \
      percent:float=Query(..., ge=0, le=100)):
   return {"name": name, "age":age, "percent": percent}

'''
Pydantic is a Python library for data parsing and validation. It uses the type hinting mechanism 
of the newer versions of Python (version 3.6 onwards) and validates the types during the runtime. 
Pydantic defines BaseModel class. It acts as the base class for creating user defined models.
'''

class Student(BaseModel):
   id: int
   name :str = Field(None, title="name of student", max_length=10)
   subjects: List[str] = []


@app.post("/students/")
async def student_data(s1: Student):
   return s1

@app.post("/students/{college}")
async def student_data(college:str, age:int, student:Student):
   retval={"college":college, "age":age, **student.dict()}
   return retval


@app.post("/students1")
async def student_data(name:str=Body(...),
marks:int=Body(...)):
   return {"name":name,"marks": marks}

@app.get("/hello_html/")
async def hello():
   ret='''
        <html>
        <body>
        <h2>Hello World!</h2>
        </body>
        </html>
    '''
   return HTMLResponse(content=ret)

@app.get("/hello5/{name}", response_class=HTMLResponse)
async def hello(request: Request, name:str):
   return templates.TemplateResponse("index.html", {"request": request, "name":name})


'''
Often it is required to include in the template response some resources that remain unchanged even 
if there is a certain dynamic data. Such resources are called static assets. Media files (.png, .jpg etc), 
JavaScript files to be used for executing some front end code, or stylesheets for formatting HTML 
(.CSS files) are the examples of static files.

In order to handle static files, you need a library called aiofiles
'''

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/hello6/{name}", response_class=HTMLResponse)
async def hello(request: Request, name:str):
   return templates.TemplateResponse("index.html", {"request": request, "name":name})

@app.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
   return templates.TemplateResponse("login.html", {"request": request})


class User(BaseModel):
   username:str
   password:str

'''
FastAPI has a Form class to process the data received as a request by submitting an 
HTML form. However, you need to install the python-multipart module. It is a streaming 
multipart form parser for Python.
'''
@app.post("/submit/", response_model=User)
async def submit(nm: str = Form(...), pwd: str = Form(...)):
   return User(username=nm, password=pwd)


'''
Unlike the Flask framework, FastAPI doesn’t contain any built-in development server. Hence we need Uvicorn. It implements ASGI standards and is lightning fast. ASGI stands for Asynchronous Server Gateway Interface.

The WSGI (Web Server Gateway Interface – the older standard) compliant web servers are not suitable for asyncio applications. Python web frameworks (such as FastAPI) implementing ASGI specifications provide high speed performance, comparable to web apps built with Node and Go.

Uvicorn uses uvloop and httptools libraries. It also provides support for HTTP/2 and WebSockets, which cannot be handled by WSGI. uvloop id similar to the built-in asyncio event loop. httptools library handles the http protocols.

The installation of Uvicorn as described earlier will install it with minimal dependencies. However, standard installation will also install cython based dependencies along with other additional libraries.

pip3 install uvicorn(standard)
'''
# Instead of starting Uvicorn server from command line, it can be launched programmatically also.
if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
