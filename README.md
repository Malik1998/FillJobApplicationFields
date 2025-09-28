# FillJobApplicationFields
This is small console application to fill job application from configuration. It's sends your resume.text to llm, to write cover letter.

# Setup files
1. Add *.tex file with latex of your resume
2. create .env file
3. fill it like this 

```
DB_FILE_NAME=preferences.json
BASE_URL=https://api.openai.com/v1
MODEL_NAME="gpt-4o-mini"

OPENAI_API_KEY=<YOUR OPENTOUTER KEY OR OPENAPI>
DEFAULT_USER_ID=<that wouldn't be used>
DEFAULT_TEXT_FILE=<filename of .tex file>
DEFAULT_LINKEDIN=<link to linkedin profile>

```

4. [OPTIONAL] add preferences.json and add fields you would like to be founf manually (w/o llm): 

```
{
    "user_id": {
        "<DEFAULT_USER_ID>": {
            "user_id": "<DEFAULT_USER_ID>",
            "first name": "<name>",
            "last name": "<surname>",
            "email": "<email>",
            "Phone number": "<phone number>",
        }
    }
}

```

# Setup environment
```
python3 -m venv create venv
source venv/bin/activate
pip3 install -r requirements.txt 

```

# Run
5. type in the terminal

```
python3 main.py --url <url>

```

--fill-in-browser -- still under construction



# Problems
1. If you have problems with selenium, just delete it from requirements.txt, code will still work, but w/o --fill-in-browser