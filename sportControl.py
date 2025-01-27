
import os
import sqlite3
import argon2
import datetime
import hashlib
from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from uuid import uuid4 
from time import time
import re
from starlette.responses import FileResponse
from typing import Annotated, Mapping
from sportModel import New_user, User, Inventory
from sportService import Create_user, Admin, get_free_inventory, get_db, get_my_inventory, get_broken_inventory,\
set_inventory, delete_inventory, view_shop_wishes, view_occupied, occupy_inventory, pass_inventory, view_need_inspection
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sport = FastAPI()

from pydantic import BaseModel

ph = argon2.PasswordHasher()

sport.mount("/", StaticFiles(directory="."), name=".")

sport.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sec = HTTPBasic()

COOKIE_ALIAS = "SKET"

session_storage: Mapping[str, str] = dict()

def check_auth(credentials: Annotated[HTTPBasicCredentials, Depends(sec)], db: sqlite3.Cursor = Depends(get_db)):
    login = credentials.email
    passw = credentials.password
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or passw", headers={"WWW_Authenticate": "Basic"})
    fetched_user = User.getByEmail(db, login)

    if fetched_user is None:
        raise exc
    is_correct = password_correct(fetched_user.password, fetched_user.salt, passw)
    if not is_correct:
        raise exc
    
    return fetched_user.id
    


def set_session(id):
    sessid = uuid4().hex
    while sessid in session_storage.keys():
        sessid = uuid4().hex
    session_storage[sessid] = str(id)
    return sessid


def get_session(sessid: str = Cookie(default=None, alias=COOKIE_ALIAS)):
    print(sessid)
    exc = HTTPException(status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    if not sessid:
        raise exc
    if re.match(r'[a-f0-9]{32}', sessid) is None:
        raise exc
    sess = session_storage.get(sessid)
    if sess is None:
        raise exc
    
    return sess


    
def rem_session(sess_data: str = Depends(get_session), sessid: str = Cookie(default=None, alias=COOKIE_ALIAS)):
    del session_storage[sessid]
    return sess_data

class Request:
    method: str
    url: str

@sport.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={"message": "Custom message for Method Not Allowed"}
        )
    return await default_http_exception_handler(request, exc)

@sport.post("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@sport.post('/auth/login')
def login(response: Response, auth: Annotated[str, Depends(check_auth)]):
    session_id = set_session(auth)
    response.set_cookie(COOKIE_ALIAS, session_id, expires=300)
    return {"success": True}

@sport.post('/auth/logout')
def login(response: Response, dropped: Annotated[str, Depends(rem_session)]):
    response.delete_cookie(COOKIE_ALIAS)
    return {"success": True, "deleted": dropped}

@sport.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

@sport.get("/")
def get_home_page():
    return {"message": "aboba"}

@sport.post("/new_user")
def new_user(data:New_user, cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        Create_user(data.name, data.password,data.email,False,cursor)
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "this user already exist"}

@sport.post("/new_admin")
def new_admin(data:New_user,credentials: Annotated[HTTPBasicCredentials, Depends(sec)], cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        if Admin(credentials.username,cursor):
            Create_user(data.name, data.password,data.email,True,cursor)
        else:
            return {"message": "only admins can make admins"}
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "this user already exist"}

@sport.get("/get_inventory")
def get_inventory(cursor: sqlite3.Cursor = Depends(get_db)):
    return {"message": get_free_inventory(cursor)}

@sport.get("/get_my_inventory")
def get_my(credentials: Annotated[HTTPBasicCredentials, Depends(sec)], cursor: sqlite3.Cursor = Depends(get_db)):
    return {"message": get_my_inventory(credentials.username,cursor)}

@sport.get("/get_broken_inventory")
def get_broken(credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    if Admin(credentials.username, cursor):
        return {"message": get_broken_inventory(cursor)}

@sport.put("/set_inventory")
def rewrite_inventory(data:Inventory ,credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        if Admin(credentials.username,cursor):
            set_inventory(data.id, data.name, data.cond, cursor)
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "something went wrong"}

@sport.put("/add_inventory")
def new_inventory(credentials: Annotated[HTTPBasicCredentials, Depends(sec)], name:str, cond:str =Form(), cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        if Admin(credentials.username,cursor):
            add_inventory(name, cond, cursor)
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "something went wrong"}

@sport.get("/view_wishes")
def view_wishes(credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        if Admin(credentials.username,cursor):
            return {"message": f"{view_shop_wishes(cursor)}"}
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "something went wrong"}

@sport.post("/send_request")
def send_request(credentials: Annotated[HTTPBasicCredentials, Depends(sec)], name:str =Form(), cursor: sqlite3.Cursor = Depends(get_db)):
    return send_request()

@sport.get("/get_occupied_inventory")
def get_occupied(credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        if Admin(credentials.username,cursor):
            return {"message": f"{view_occupied(cursor)}"}
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "something went wrong"}

@sport.get("/get_need_inspection")
def get_need_inspection(credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    try:
        if Admin(credentials.username,cursor):
            return {"message": f"{view_need_inspection(cursor)}"}
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
        return {"message": "something went wrong"}

@sport.post("/return_inventory")
def return_inventory(inventory_name:str, credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    pass_inventory(inventory_name, credentials.username, cursor)

@sport.post("/occupy_inv")
def occupy_inv(inventory_name:str, credentials: Annotated[HTTPBasicCredentials, Depends(sec)],cursor: sqlite3.Cursor = Depends(get_db)):
    occupy_inventory(inventory_name, credentials.username, cursor)

