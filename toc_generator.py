import os
import re
from pprint import pprint

"""The main purpose is to generate human readable Table Of Content"""


TEMPLATE_FILENAME = "template.md"

INTERVIEW_FOLDER = "interview"
TEST_ASSIGNMENT_FOLDER = "test_assignments"

LANGUAGE_REGEX = r"(\.(\w+))?\.md"

TOC_FILENAME = "toc{language}.md"

# Folders to be listed in TOC
LISTED_FODLERS = (INTERVIEW_FOLDER, TEST_ASSIGNMENT_FOLDER)

IGNORABLE_FILES = [TEMPLATE_FILENAME, ".gitkeep"]


def capitalize_snake_case(string: str) -> str:
    return " ".join([value.capitalize() for value in string.replace("_", " ").split()])


def is_dir_should_be_listed(files: list):
    are_files_presented = bool(files)
    is_ignore_by_rules = bool(set(files).intersection(IGNORABLE_FILES))
    return are_files_presented and not is_ignore_by_rules


def update_dict(d, keys, value):
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    if keys[-1] in d:
        if isinstance(d[keys[-1]], list):
            d[keys[-1]].append(value)
        else:
            d[keys[-1]] = [d[keys[-1]], value]
    else:
        d[keys[-1]] = value


def generate_data_dict_per_folder(folder):
    result = {}

    for dirpath, _, files in os.walk(folder):
        if is_dir_should_be_listed(files):
            for file in files:
                match = re.search(LANGUAGE_REGEX, file)
                if match:
                    language_group = match.group(2) or "en"
                    path_components = os.path.relpath(dirpath, folder).split(
                        os.path.sep
                    )
                    dict_formation_components = path_components[:-1]
                    update_dict(
                        result,
                        [language_group] + dict_formation_components,
                        {file: dirpath},
                    )
    return result


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

    print(overall_data_dict)
    for language in available_languages:
        filename_by_language = TOC_FILENAME.format(
            language="" if language == "en" else f".{language}"
        )
        with open(filename_by_language, "w", encoding="utf-8") as toc_language:
            for folder, available_folder_data in overall_data_dict.items():
                toc_language.write(f"## {capitalize_snake_case(folder)}\n\n")

                data_by_language = available_folder_data.get(language)
                if data_by_language:
                    for subsection, questions in data_by_language.items():
                        toc_language.write(f"### {capitalize_snake_case(subsection)}\n")
                        for question in questions:
                            for name, path in question.items():
                                file_path = os.path.join(path, name)

                                file_header = None
                                with open(
                                    file=file_path, mode="r", encoding="utf-8"
                                ) as current_file:
                                    match = re.search("#\s(.*)\n", current_file.read())
                                    if match:
                                        file_header = match.group(1)

                                toc_language.write(
                                    f"* [{file_header or capitalize_snake_case(name)}](./{file_path})\n"
                                )
                toc_language.write("\n")


generate_toc_file()
