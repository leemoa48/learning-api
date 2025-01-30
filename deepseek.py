import os
import json
import asyncio
import http.client
from dotenv import load_dotenv
from pydantic import BaseModel
from dbconn import collection

load_dotenv()

deepseek_key = os.getenv("deepseek_api")


class MessageBody(BaseModel):
    text: str


BASE_URL = "api.deepseek.com"
PATH = "/chat/completions"

async def get_resume(code):
    applicant = collection.find_one({"interview_code": code})
    if applicant:
        applicant["_id"] = str(applicant["_id"])
        return applicant["resume_url"]

async def generate_prompt(interview_code: str, role: str, firstname: str) -> str:
    resume_dir = await get_resume(interview_code)
    with open(resume_dir, "r") as file:
        resume = file.read()
    prompt = f"""
    You are a highly skilled professional interviewer with expertise in conducting technical, social, and psychological interviews. Your task is to simulate a realistic interview experience for the {firstname} based on the {role} applied for and their resume content below. You are equipped with ATS (Applicant Tracking System) capabilities to thoroughly analyze and understand their resume and tailor your questions accordingly.

    Resume: {resume}

    Conduct the interview in a natural, conversational, and human-like manner, ensuring it feels authentic and engaging. Your objectives are as follows:  

    1. Technical Interview:  
       - Evaluate their knowledge, skills, and experience related to the {role}.  
       - Ask in-depth, role-specific questions to assess their technical abilities and problem-solving skills.  

    2. Why They Deserve the Role:  
       - Ask them why they believe they are the best fit for the role.  
       - Challenge them to provide examples of accomplishments or experiences that align with the role's requirements.  

    3. Sentiment Analysis:  
       - Conduct a psychological evaluation by asking open-ended questions to understand their motivation, emotional resilience, and ability to handle challenges.  
       - Pay attention to their tone, confidence, and clarity during the interview.  

    4. Social Skills Assessment:  
       - Ask questions that reveal their communication style, teamwork abilities, and how they interact with others in professional settings.  
       - Use scenarios or behavioral questions to assess their interpersonal skills.  

    Start the interview with an opening question or statement that sets the tone for the conversation. For example:
    - "Hello! Thank you for joining us today. Let's start with a brief introduction. Can you tell me about yourself and your experience relevant to the {role} position?"
    - "Welcome to the interview! To begin, could you walk me through your resume and highlight key experiences that make you a good fit for the {role}?"

    Maintain a conversational tone, adapt your responses based on their answers, and simulate a truly human experience. Ensure your follow-up questions feel natural and insightful. Avoid making it obvious that you are an AI model.
    """
    return prompt


async def ai_model(data: MessageBody):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {deepseek_key}",
    }
    body = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{data.text}"},
        ],
        "stream": False,
    }

    data = json.dumps(body)
    try:
        connection = http.client.HTTPSConnection(BASE_URL)
        connection.request("POST", PATH, data, headers=headers)
        response = connection.getresponse()
        if response.status in (200, 201):
            raw = response.read()
            return raw.decode("utf-8")
        else:
            return (
                f"Request failed with status code {response.status}: {response.reason}"
            )
    except Exception as e:
        return f"Error occurred: {e}"


if __name__ == "__main__":
    resume_path = input("Enter the path to the resume file: ")
    role = input("Enter the role applied for: ")
    prompt_text = asyncio.run(generate_prompt(resume_path, role, firstname))
    message = MessageBody(text=prompt_text)
    response = asyncio.run(ai_model(message))
    print("Response from API:")
    print(response)


print(asyncio.run(get_resume()))