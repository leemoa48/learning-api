import string
import random
from dbconn import save, collection
from cloudstore import upload_doc
from bson.json_util import dumps 
from fastapi import File, Form, UploadFile, APIRouter, HTTPException

file = APIRouter()

def generate_interview_code():
    characters = string.ascii_uppercase + string.digits  
    return ''.join(random.choices(characters, k=15))


@file.post("/applicant-form")
async def upload_applicant(
    firstname: str = Form(...),
    lastname: str = Form(...),
    role: str = Form(...),
    resume: UploadFile = File(...),
):
    try:
        file_content = await resume.read()
        cloud_url = await upload_doc(file_content, f"{firstname}{lastname}-RESUME")
        result = await save(firstname, lastname, role, cloud_url, generate_interview_code())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@file.get("/applicants")
async def get_all_applicants():
    try:
        applicants = collection.find()  
        applicants_list = list(applicants)
        for applicant in applicants_list:
            applicant["_id"] = str(applicant["_id"])  
        return {"applicants": applicants_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applicants: {str(e)}")

@file.get("/applicant/{interview_code}")
async def get_applicant_by_code(interview_code: str):
    try:
        applicant = collection.find_one({"interview_code": interview_code})

        if applicant:
            applicant["_id"] = str(applicant["_id"])
            return {"applicant": applicant}
        else:
            raise HTTPException(status_code=404, detail="Applicant not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applicant: {str(e)}")
