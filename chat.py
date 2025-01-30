from fastapi import APIRouter, WebSocket
from deepseek import ai_model, MessageBody

chat = APIRouter()


@chat.websocket("/room")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message = MessageBody(text=data)
        ai_response = await ai_model(message)
        await websocket.send_text(ai_response)
