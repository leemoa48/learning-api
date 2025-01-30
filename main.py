import json
import uvicorn
from process import file
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Learning API",
    description="An AI platform powered by deepseek at it core to simulate iterview prep jobseekers before the actual interview",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(file)

@app.get("/")
async def main():
    content = json.dumps({"message": "Server is working fine"})
    return Response(content=content, status_code=status.HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
