import json
import uuid
import os
from dotenv import load_dotenv  

load_dotenv()
DB_FILE_NAME = os.getenv("DB_FILE_NAME", "preferences.json")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "user")
DEFAULT_TEXT_FILE =  os.getenv("DEFAULT_TEXT_FILE", "resume.tex")
DEFAULT_LINKEDIN = os.getenv("DEFAULT_LINKEDIN", "")

with open(DEFAULT_TEXT_FILE, "r") as fp:
    DEFAULT_RESUME_LATEX_DATA = "\n".join(fp.readlines())

DEFAULT_USER_INFO = {
        "user_id": DEFAULT_USER_ID,
        "resume_latex_data": DEFAULT_RESUME_LATEX_DATA,
        "linkedin": DEFAULT_LINKEDIN
}

DB = None
def get_db():
    global DB
    if DB is None:
        try:
            with open(DB_FILE_NAME, "r") as fp:
                DB = json.load(fp)
        except Exception as e:
            print(e)
            DB = dict()
    return DB

def rewrite_db():
    global DB
    with open(DB_FILE_NAME, "w") as fp:
        json.dump(DB, fp, indent=4)
    DB = None


def get_user_info(user_id: str) -> dict:
    global DB
    DB = get_db()
    return DB["user_id"].get(user_id, DEFAULT_USER_INFO)


def put_user_info(user_id: str, dct: dict):
    global DB
    DB = get_db()
    if "user_id" not in DB:
        DB["user_id"] = dict()
    if user_id not in DB["user_id"]:
        DB["user_id"][user_id] = dict()
    DB["user_id"][user_id].update(dct)
    rewrite_db()
    return None


def put_default_user_info():
    put_user_info(user_id=DEFAULT_USER_ID, dct = DEFAULT_USER_INFO)
    return None
    

def make_password(user_id: str) -> str:
    return str(uuid.uuid4())


def get_job_key_from_db(url, key="history"):
    global DB
    DB = get_db()
    if "history" not in DB:
        DB["history"] = {"user_id": dict()}
        rewrite_db()
        return None
        
    for list_of_jobs in DB["history"]["user_id"].values():
        for elem in list_of_jobs:
            if url == elem["url"] and elem.get(key) != None:
                return elem.get(key)

    return None


def get_cover_letter(user_id, url):
    global DB
    DB = get_db()
    for elem in DB["history"]["user_id"].get(user_id, []):
        if url == elem["url"] and elem.get("cover_letter") != None:
            return elem.get("cover_letter")

    return None


def add_history_key(user_id, url, value, key="job_description"):
    global DB
    DB = get_db()
    if "history" not in DB:
        DB["history"] = {"user_id": dict()}
    lst = DB["history"]["user_id"].get(user_id, [])
    try:
        index = ([url == d["url"] for d in lst]).index(True)
    except ValueError:
        index = -1
    if index != -1:
        lst[index].update({"url": url, key: value})
    else:
        lst.append({"url": url, key: value})
    DB["history"]["user_id"][user_id] = lst
    rewrite_db()