import argparse
import json
import os
from dotenv import load_dotenv
from fill_fields import fill_all_fields_by_llm, is_usefull_for_future
from db import get_user_info, put_default_user_info, add_history_key, put_user_info
from web_browser import open_and_capture, fill_field_from_dict, get_job_description, get_fields_forms_to_fill

# Load environment variables
load_dotenv()
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "some_user_name")

parser = argparse.ArgumentParser(description="Job Application Filling")
parser.add_argument("--url", type=str, help="URL for job description (also page with forms to fill)",
                    default="https://careers.withwaymo.com/jobs/maching-learning-engineer-planner-selection-mountain-view-california-united-states?gh_jid=7170802#apply")
parser.add_argument("--fill-in-browser", action="store_true", help="Flag to fill fields directly in browser")

def main():
    args = parser.parse_args()
    url = args.url
    put_default_user_info()

    job_description = get_job_description(url)
    add_history_key(DEFAULT_USER_ID, url, job_description, key="job_description")

    fields = get_fields_forms_to_fill(url)
    fields = json.loads(fields.replace("```", "").replace("json", "")) if isinstance(fields, str) else fields

    add_history_key(DEFAULT_USER_ID, url, fields, key="fields")

    filled_data = fill_all_fields_by_llm(fields, get_user_info(DEFAULT_USER_ID), job_description, url)
    if args.fill_in_browser:
        _, driver = open_and_capture(url, headless=False)
    for k, v in filled_data.items():
        print(f"{k}:\n {v}\n\n")
        add_history_key(DEFAULT_USER_ID, url, v, key=k)
        if is_usefull_for_future(k):
            put_user_info(DEFAULT_USER_ID, {k: v})
        if args.fill_in_browser:
            fill_field_from_dict(driver, k, v)

if __name__ == "__main__":
    main()