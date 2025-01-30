import os
import asyncio
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from pymongo import MongoClient

# url parameters
uri = os.getenv("MONGO_URI")

# create a client 
client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)

# create a database and a collection
db = client["Apllicant"]
print("✅ Connected to MongoDB successfully!")

# this act as our curse just like in sql
collection = db.applicants


# Save function
async def save(firstname, lastname, role, cv_url, interview_code):
    applicant_data = {
        "firstname": firstname,
        "lastname": lastname,
        "role": role,
        "resume_url": cv_url,
        "interview_code": interview_code,
    }
    try:
        # Insert data into the 'applicants' collection
        result = collection.insert_one(applicant_data)
        return "saved"
    except Exception as e:
        return f"Error saving applicant data: {str(e)}"


if __name__ == "__main__":
    print(asyncio.run(save("victor", "chib", "dev", "https://hg.com", "AFSASFDED")))
