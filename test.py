from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Указываем папку, где лежат статические файлы
app.mount("/", StaticFiles(directory="."), name=".")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request:
    method: str
    url: str


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Модели данных
class SignUpData(BaseModel):
    username: str
    email: str
    password: str

class SignInData(BaseModel):
    email: str
    password: str

@app.post("/signup")
async def signup(data: SignUpData):
    print("Received signup data:", data)
    return {"message": "Registration successful"}


@app.post("/signin")
async def signin(data: SignInData):
    print("Received signin data:", data)
    return {"message": "Login successful"}

@app.get("/ping")
async def ping():
    print("Ping received")
    return {"message": "pong"}

class TestData(BaseModel):
    message: str

@app.post("/test1")
async def test_endpoint(data: TestData):
    print("Received POST request on /test")
    print(f"Data: {data}")
    return {"response": f"You sent: {data.message}"}



