from fill_fields import is_cover_letter, is_cv
import time
import requests
from llm import make_llm_call
from html_to_markdown import convert_to_markdown
from db import get_job_key_from_db



def open_and_capture(url, headless="new"):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    # options.add_argument(f"--headless={headless}")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    
    driver.get(url)
    return capture(driver)

def capture(driver):
    time.sleep(2)  # wait for the page to load
    html_content = driver.page_source
    return html_content, driver

def get_and_click_all_accept_buttons(driver):
    try:
        # Find all buttons on the page
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons on the page.")
        
        # Iterate through each button and click it
        for index, button in enumerate(buttons):
            try:
                if button.text.lower() in ["accept", "agree", "i accept", "i agree"]:
                    print(f"Clicking button {index + 1}: {button.text}")
                    button.click()
            except Exception as e:
                print(f"Could not click button {index + 1}: {e}")
    except Exception as e:
        print(f"Error while getting buttons: {e}")

def delete_all_special_characters(text):
    return ''.join(e for e in text if e.isalnum()).strip()

def is_almost_equal(str1, str2, threshold=0.8):
    str1, str2 = delete_all_special_characters(str1.lower()), delete_all_special_characters(str2.lower())
    if str1 == str2:
        return True
    len1, len2 = len(str1), len(str2)
    if abs(len1 - len2) > max(len1, len2) * (1 - threshold):
        return False
    matches = sum(1 for a, b in zip(str1, str2) if a == b)
    similarity = matches / max(len1, len2)
    return similarity >= threshold

def fill_field_from_dict(driver, field_name, field_value):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    get_and_click_all_accept_buttons(driver)
    if is_cv(field_name) or is_cover_letter(field_name):
        print(f"Don't fill {field_name} automatically")
        return
    is_filled = False
    for input_el in driver.find_elements(By.TAG_NAME, "input"):
        label = input_el.get_attribute("placeholder") or input_el.get_attribute("aria-label")
        if label and (field_name.lower() in label.lower() or is_almost_equal(label, field_name)):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", input_el)
                WebDriverWait(driver, 10).until(EC.visibility_of(input_el))
                input_el.clear()
                input_el.send_keys(field_value)
                print(f"Filled '{field_name}' with '{field_value}'")
                is_filled = True
                return
            except Exception as e:
                print(f"Could not fill field '{field_name}': {e}")
                return
    if not is_filled:
        print(f"Could not find field '{field_name}' to fill.")



def get_job_description(url):
    cached = get_job_key_from_db(url, "job_description")
    if cached is not None:
        return cached
    
    html = requests.get(url).text
    markdown = convert_to_markdown(html)
    if markdown.replace(" ", ""):
        markdown = html
    prompt = f"""
    You are a helpful assistant that can help find full job description from html.
    Return only job description from {markdown}
    """
    return make_llm_call(prompt)


def get_fields_forms_to_fill(url):
    cached = get_job_key_from_db(url, "fields")
    if cached is not None:
        return cached
    
    html = requests.get(url).text
    markdown = convert_to_markdown(html)
    if markdown.replace(" ", ""):
        markdown = html
    prompt = f"""
    You are a helpful assistant that can help find all froms to be filled while applying to the job
    Output must look like: 
    ```json
    ["field1", "field2", "field3"]
    ```
    F.E: ```json
    ["Full Name", "email", "cover letter", "resume"]
    ```

    Return only fields in json format from "{markdown}"


    """
    return make_llm_call(prompt)

