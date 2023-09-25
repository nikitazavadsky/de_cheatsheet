import os
from typing import Dict
import re

"""The main purpose is to generate human readable Table Of Content"""

HEADER_ONE = '#'
HEADER_TWO = '##'
BULLETED_LIST = '*'

TEMPLATE_FILENAME = 'template.md'

INTERVIEW_FOLDER = 'interview'
TEST_ASSIGNMENT_FOLDER = 'test_assignments'

LANGUAGE_REGEX = r'(\.(\w+))?\.md'

TOC_FILENAME = 'toc{language}.md'

# Folders to be listed in TOC
LISTED_FODLERS = (INTERVIEW_FOLDER, TEST_ASSIGNMENT_FOLDER)

def capitalize_snake_case(string: str) -> str:
    return ' '.join([value.capitalize() for value in string.replace('_', ' ').split()])

def generate_data_dict_per_folder(folder):
    data = {}
    for dirpath, _, files in os.walk(folder):
        if len(files) != 0 and TEMPLATE_FILENAME not in files:
            for file in files:
                match = re.search(LANGUAGE_REGEX, file)
                if match:
                    language_group = match.group(2) or 'en'
                    if language_group not in data:
                        data[language_group] = {}
                    data[language_group][dirpath] = file


    return data

def generate_overall_data_dict():
    overall_datadict = dict()
    for folder in LISTED_FODLERS:
        current_data_dict = generate_data_dict_per_folder(folder=folder)
        if current_data_dict:
            overall_datadict[folder] = current_data_dict
    
    return overall_datadict

def generate_toc_file():
    overall_data_dict = generate_overall_data_dict()

    # Get available languages
    available_languages = []
    for _, available_folder_data in overall_data_dict.items():
        available_languages.extend(available_folder_data.keys())
    
    
    for language in available_languages:
        filename_by_language = TOC_FILENAME.format(
            language = '' if language == 'en' else f".{language}"
            )
        with open(filename_by_language, 'w', encoding='utf-8') as toc_language:
            for folder, available_folder_data in overall_data_dict.items():
                toc_language.write(f"{HEADER_TWO} {folder.capitalize()}\n\n")
                
                data_by_language = available_folder_data.get(language)
                if data_by_language:
                    for folder_path, file in data_by_language.items():
                        list_entry = capitalize_snake_case(os.path.split(folder_path)[-1])

                        file_path = os.path.join(folder_path, file)
                        
                        file_header = None
                        with open(file=file_path, mode='r', encoding='utf-8') as current_file:
                            match = re.search("#\s(.*)\n", current_file.read())
                            if match:
                                file_header = match.group(1)
                            
                        toc_language.write(f"* [{file_header or list_entry}](./{file_path})\n")
                toc_language.write("\n")


generate_toc_file()