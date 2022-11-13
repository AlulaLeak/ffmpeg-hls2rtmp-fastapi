from fastapi import FastAPI
from pydantic import BaseModel
from subprocess import Popen
import aiohttp

# Creating FastAPI instance
app = FastAPI()

# Creating class to define the request body
class request_body(BaseModel):
    room_name : str
    stream_url : str

# Creating an Endpoint to receive the data
@app.post('/create')
async def create(data : request_body):

    # Making the data in a form suitable
    room_name = data.room_name
    stream_url = data.stream_url

    # Recieve Secret Key from Broadcase Server
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://localhost:8090/control/get?room={room_name}') as resp:
            response_json = await resp.json()
            secret_key = response_json['data']

    # Start Subprocess (FFMpeg Encoding From HLS to RTMP before sending to Broadcasting Server)
    Popen(["ffmpeg","-re", "-nostdin", "-i", stream_url, "-vcodec", "libx264", "-preset:v", "ultrafast", "-acodec", "aac", "-f", "flv", f"rtmp://localhost:1935/zoo/{secret_key}"])
    # Return the Result
    return { 'Stream Available At' : f"http://127.0.0.1:7002/zoo/{room_name}.m3u8"}
