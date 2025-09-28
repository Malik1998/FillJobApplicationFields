from db import make_password, get_job_key_from_db
from llm import make_llm_call, make_structured_call

import base64




def is_cover_letter(field_name: str) -> bool:
    return "cover" in field_name.lower()


def is_password(field_name: str) -> bool:
    return "password" in field_name.lower()

def get_cover_letter_by_llm(user_info: dict, job_description: str, url: str) -> str:
    cached_cover_letter = get_job_key_from_db(url, key="cover_letter")
    if cached_cover_letter is not None:
        return cached_cover_letter

    prompt = f"""
    You are a helpful assistant that can create a cover letter for the user. That make him more attractive to the employer.
    The user has the following information: {user_info}
    The job description is: {job_description}
    Don't add information or placeholder of information you didn't know
    """
    return make_llm_call(prompt)

def is_cv(field_name):
    return "resume" in field_name.lower() or "cv" in field_name.lower()

def get_by_field_by_llm(field_name: str, user_info: dict, job_description: str, url: str) -> str:
    if is_cover_letter(field_name):
        return get_cover_letter_by_llm(user_info, job_description=job_description, url=url)

    if is_cv(field_name):
        # TODO: maybe make personalsed resume
        return user_info.get("resume_file_name", "path_to_resume.pdf")

    if is_password(field_name):
        return make_password(user_info["user_id"])

    for k, v in user_info.items():
        if v is not None:
            if k.lower() in field_name.lower() or field_name.lower() in k.lower():
                return v

    prompt = f"""
    You are a helpful assistant that can help me find the appropriate field for the user.
    The user is a person who is looking for a job.
    The user has the following information: {user_info}
    The field name is: {field_name}
    Give only calculated field value
    """
    return make_llm_call(prompt)


def is_usefull_for_future(field_name):

    #TODO: maybe make a call to llm
    return not(is_cover_letter(field_name) or is_cv(field_name) or is_password(field_name))


def fill_all_fields_by_llm(fields: list[str], user_info: dict, job_description: str, url: str) -> dict:
    return {field: get_by_field_by_llm(field, user_info, job_description=job_description, url=url) for field in fields}


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def extract_fields_from_image(image_path, html_content: str):
    base64_image = image_to_base64(image_path)
    messages = [
            {"role": "system", "content": "You are an assistant that extracts form field names and placeholders from images."},
            {"role": "user", "content": [
                {"type": "text", "text": "Parse this form image and return a JSON list like: [{label: 'field name', value: 'John Doe'}]"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                {"type": "text", "text": html_content}
            ]}
        ]
    return make_structured_call(messages)
    