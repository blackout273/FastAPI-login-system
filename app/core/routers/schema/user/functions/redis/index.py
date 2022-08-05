from distutils.debug import DEBUG
import json
import aioredis, logging
redis= aioredis.from_url(url="redis://localhost:6379/0", decode_responses=True)
logging.basicConfig(filename="D:/python/sessions/venv/app/core/routers/schema/user/functions/redis/logs/systemLogs.log", level=logging.DEBUG)

async def create(idSession, data):
    search= await redis.exists(f"{idSession}")
    try:
        if search == 0:
            await redis.set(f"{idSession}",json.dumps(data),600)
            logging.debug(msg="Salvou no Redis")
            
        else:
            return None
    except Exception as ex:
        return ex
    finally:
        return search


async def delete(idSession):
    search= await redis.exists(f"{idSession}")
    if search==1:
        await redis.delete(f"{idSession}")
        logging.debug(msg="Deletou no Redis")
    else:
        return {"Message":"Session not Provided"}

async def get(idSession)->dict:
    search= await redis.exists(f"{idSession}")
    if search==1:
        result= await redis.get(f"{idSession}")
        logging.debug(msg="Buscou no Redis")
        return {"usuario":json.loads(result) }
    return None

async def update(idSession, data, newIdSession):
    search= await redis.exists(f"{idSession}")
    if search==1:
        await redis.delete(f"{idSession}")
        await redis.set(f"{newIdSession}",json.dumps(data),600)
        search= await redis.exists(f"{newIdSession}")
        logging.debug(msg="Atualizou no Redis")
    else:
        return {"Message":"Invalid Session"}
