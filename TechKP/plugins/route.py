import re, math, logging, secrets, mimetypes, time
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from KPBOT.bot import multi_clients, work_loads, TechKPBot
from KPBOT.server.exceptions import FIleNotFound, InvalidHash
from KPBOT import StartTime, __version__
from KPBOT.util.custom_dl import ByteStreamer
from KPBOT.util.time_format import get_readable_time
from KPBOT.util.render_template import render_page
from TechKP.config.config import Config
routes = web.RouteTableDef()


from aiohttp import web
import motor.motor_asyncio


client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URI)
db = client[Config.SESSION_NAME]
collection = db[Config.COLLECTION_NAME]

def serialize_document(doc):
    """Convert MongoDB document to a serializable format."""
    doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return doc


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("BenFilterBot")

@routes.get(r"/miniapp", allow_head=True)
async def miniapp_handler(request: web.Request):
    return web.Response(text=open('KPBOT/template/miniapp.html').read(), content_type='text/html')

@routes.get(r"/search", allow_head=True)
async def search_handler(request: web.Request):
    query = request.query.get('query', '')
    page = int(request.query.get('page', 1))
    limit = int(request.query.get('limit', 10))
    skip = (page - 1) * limit

    if not query:
        return web.json_response({'items': [], 'hasPrev': False, 'hasNext': False})
    
    total_count = await collection.count_documents({'file_name': {'$regex': query, '$options': 'i'}})
    cursor = collection.find({'file_name': {'$regex': query, '$options': 'i'}}).skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)
    
    has_prev = page > 1
    has_next = skip + limit < total_count

    return web.json_response({
        'items': [
            {
                'file_id': doc.get('file_id', ''),
                'file_name': doc.get('file_name', '')
            }
            for doc in results
        ],
        'hasPrev': has_prev,
        'hasNext': has_next
    })


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if Config.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
