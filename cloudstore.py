import os
import asyncio
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True,
)

async def upload_doc(file, name: str):
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            public_id=name,
            resource_type="auto",
            use_filename=True,
            unique_filename=False,
            pages=True,
        )
        return upload_result["secure_url"]
    except Exception as e:
        print(f"An error occurred during upload: {str(e)}")
        return None
# print(cloud("C:/Users/VICTOR/Desktop/dfweb/static/dfi.png", "profile"))
