from datetime import datetime, timedelta
import logging, jwt, os
from uuid import UUID, uuid4
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from app.core.routers.schema.user.models.baseModel import models as model
from app.core.routers.schema.user.functions import index as functions
from app.core.routers.schema.user.functions.redis import index as serviceRedis
JWT_KEY = os.environ.get("JWT_KEY")
logging.basicConfig(filename="D:/python/sessions/venv/app/core/routers/schema/user/functions/redis/logs/systemLogs.log", level=logging.DEBUG)

v=dict()


router = APIRouter()
@router.post("/login")
async def main(data:model.Login,idSession:UUID = Depends(functions.Cookies)):
    logging.debug(msg=f"Usuario {data.usuario} solicitou login as {datetime.now()}")
    await serviceRedis.delete(idSession)
    message="sucesso"
    try:
        Idsession = uuid4()
        dataJWT = functions.getTokens({"nome":data.usuario})
            
    except Exception as ex:
        message=f"{ex}"    
    finally:
        jsonResponse=  JSONResponse(
            content={
                "status":200,
                "payload":dataJWT,
                "message":message
                }
                )
        if jsonResponse.status_code==200:
            jsonResponse.set_cookie(key="cookie", value=Idsession, expires=900, secure=False, httponly=True)
            await serviceRedis.create(Idsession,dataJWT) 
        return jsonResponse
        

@router.post("/retornaDados",dependencies=[Depends(functions.Cookies)])
async def main(request:Request,idSession:UUID = Depends(functions.Cookies)):
    
    data={"code":None,"status":None}
    message="Success"
    try:
        dataEncoded = await serviceRedis.get(idSession)
        data= functions.openData(dataEncoded["usuario"])
    except Exception as ex:
        message=f"{ex}"    
        data["code"]= 400
    finally:
        jsonResponse=  JSONResponse(
            content={
                "status":data["code"],
                "payload":data["status"],
                "message":message
                }
                )     
        return jsonResponse


@router.post("/logout",dependencies=[Depends(functions.Cookies)])
async def main(idSession:UUID = Depends(functions.Cookies)):
    code=None
    message=None
    try:
        data = await serviceRedis.get(idSession)
        logging.debug(msg=f"Usuario {functions.openData(data['usuario'])['status']['nome']} solicitou logout as {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        message="Desconectado"
        code=200      
    except Exception as ex:
        message=f"{ex}"
        code=400   
    finally:
        jsonResponse=  JSONResponse(
            content={
                "status":code,
                "message":message
                }
                )
        if jsonResponse.status_code==200:
            jsonResponse.delete_cookie(key="cookie")
            await serviceRedis.delete(idSession)    
        return jsonResponse

@router.post("/refresh",dependencies=[Depends(functions.Cookies)])
async def main(idSession:UUID = Depends(functions.Cookies)):
    payload=None
    code=None
    message=None
    jsonresponse=None
    newIdSession = uuid4()
    try:
        code=200
        message="success"
        data = await serviceRedis.get(idSession)
        for search in [data["usuario"]["refreshToken"],data["usuario"]["accessToken"]]:
            raw_data = jwt.decode(jwt=search, key=JWT_KEY, algorithms="HS256",leeway=300, options={"verify_signature":True})
            if raw_data["type"]=="refreshToken":
                if datetime.utcfromtimestamp(raw_data["exp"]-10800)> datetime.utcnow()-timedelta(hours=3):
                    logging.info(msg=f"refresh token vai expirar em {datetime.utcfromtimestamp(raw_data['exp']).strftime('%d-%m-%Y %H:%M:%S')} ")
                else:
                    raise Exception('desconectado')
            if raw_data["type"]=="accessToken":
                logging.info(msg=f"Access token vai expirar em {datetime.utcfromtimestamp(raw_data['exp']).strftime('%d-%m-%Y %H:%M:%S')} ")
                payload=raw_data['nome']
                jsonresponse= JSONResponse(content={"status":code, "message":message, "payload":payload})
    
                newDataJWT = functions.getTokens({"nome":payload})
                jsonresponse.delete_cookie("cookie")
                jsonresponse.set_cookie(key="cookie", value=newIdSession, expires=900, secure=False, httponly=True)
                await serviceRedis.update(idSession,newDataJWT , newIdSession)
                
                

    except Exception as ex:
        message=f"{ex}"
        code=400 
    finally:
        
        return jsonresponse