import mysql.connector
import jwt, datetime, os, json, ast
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from fastapi import Request
from jwt.exceptions import ExpiredSignatureError
from app.config.connector.database import index as connector
from app.core.routers.schema.user.functions.redis import index as serviceRedis

from urllib.error import HTTPError
JWT_KEY = os.environ.get("JWT_KEY")

def getTokens(data):
    payloadAccess={
        "nome":data["nome"], 
        "iat":datetime.utcnow(),
        "exp":datetime.utcnow() + timedelta(minutes=1),
        "type":"accessToken"
    }
    payloadRefresh={
        "nome":data["nome"], 
        "iat":datetime.utcnow(),
        "exp":datetime.utcnow() + timedelta(minutes=10),
        "type":"refreshToken"
    }
    accessToken= jwt.encode(payload=payloadAccess, key=JWT_KEY, algorithm="HS256")
    refreshToken = jwt.encode(payload=payloadRefresh, key=JWT_KEY, algorithm="HS256")
    return {
        "accessToken":accessToken,
        "refreshToken":refreshToken
    }

def toDataBase(data): 
    cnx = connector.connect()
    cursor = cnx.cursor()
    
    query_insert=f""" INSERT INTO session(sessionID) VALUES (%s)"""
    cursor.execute(query_insert, data)
    cnx.commit()

    query="SELECT COUNT(*) FROM session"
    cursor.execute(query)

    myresult = cursor.fetchall()

    for x in myresult:
        print(x)
        
    cursor.close()
    cnx.close()

def openData(token):
    code=None
    decoded=None
    try:
        decoded = jwt.decode(jwt=token['accessToken'], key=JWT_KEY, algorithms="HS256",leeway=300, options={"verify_signature":True})
        code = 200
    except ExpiredSignatureError as ex:
        decoded = f"{ex}"
        code=400
    finally:
        return {"status":decoded,"code":code}

async def Cookies(req:Request):
    
    result=None
    check = req.cookies.get("cookie")
    try:
        if check== None: 
            result=  Exception("not session provided")
        result = check
    except Exception as ex:
        result = f"{ex}"
    finally:
        return result