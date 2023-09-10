import os, json, re
from typing import Any
from fastapi import FastAPI

## Defining gloabal accessible data here:

# Location of all json files:
JSON_FILE_LOCATION = "patent_jsons"

# List of all the json:
PATENT_DATA_NAME_DICT = {}

# Intializing fastapi app
app = FastAPI()


# This funtion is to remove the unnecessary markup tags from the content.
async def remove_markup(text):
    # We consider the content in enclosed in <> as tags:
    pattern = r"<(.*?)>"
    # Finding all the tags in the file:
    matched_subtring = re.findall(pattern, text)
    # As tags can be repeated, we take only unique tags:
    for sub_string in set(matched_subtring):
        # Replace those with spaces in the docs.
        text = text.replace("<%s>" % sub_string, "")
    return text


# This funciton to extract content from the json file:
async def extract_info(file_content: Any) -> str:
    file_info = ""
    # If the object is of type dict we iterate over values and extract text:
    if isinstance(file_content, dict):
        for elements in file_content.values():
            file_info += await extract_info(elements)
    # It object is of type list we take all the element and extract values:
    elif isinstance(file_content, list):
        for elements in file_content:
            file_info += await extract_info(elements)
    else:
        # Else we convert value to str:
        content = str(file_content)
        # Check if content is greater than 2 to remove lang values as they are unncessary:
        if len(content) > 2:
            # Replacing all newline with spaces:
            file_info += " " + content.replace("\n", " ")
    return file_info


# On application startup load all files into the memory:
@app.on_event("startup")
async def read_file() -> None:
    # get all the files from the folder
    for file in os.listdir(JSON_FILE_LOCATION):
        # get the full path of the file:
        full_path = "%s/%s" % (JSON_FILE_LOCATION, file)
        # Open file with utf-8 encoding for character in other language:
        with open(full_path, encoding="utf-8") as file_content:
            # load file into json object
            json_content = json.load(file_content)
            # extract text that we need to search in:
            file_info = await extract_info(json_content)
            # remove markup tags in extracted text:
            file_info = await remove_markup(file_info)
            # add this to patent_json file:
            PATENT_DATA_NAME_DICT[file] = file_info


@app.get("/search")
async def search_keyword(keyword: str):
    # Replacing all newline with spaces:
    keyword = keyword.replace("\n", " ")
    # Matched docs string:
    matched_docs = []
    for file_name, file_content in PATENT_DATA_NAME_DICT.items():
        if keyword in file_content:
            matched_docs.append(file_name)
    return matched_docs
