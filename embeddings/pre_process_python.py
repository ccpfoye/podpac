
import json
import re
import os
from find_nearest_embedding import clean_string


def split_section_content(content, max_tokens=5000):
    tokens = content.split("\n")
    parts = []
    current_part = ""

    for token in tokens:
        if len(current_part) + len(token) + 1 > max_tokens:  # +1 for newline character
            parts.append(current_part.strip())
            current_part = ""

        current_part += token + "\n"

    if current_part.strip():
        parts.append(current_part.strip())

    return parts


def process_python_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    file_name = os.path.basename(file_path)
    sections = {}

    # Find classes
    class_pattern = r'^(\s*)class\s+(\w+)\s*.*:'
    classes = re.findall(class_pattern, content, flags=re.MULTILINE)

    # Find functions
    function_pattern = r'^\s*def\s+(\w+)\s*\((.*?)\)\s*:'
    functions = re.findall(function_pattern, content, flags=re.MULTILINE)

    for class_indent, class_name in classes:
        class_content = re.search(r'^{}class\s+{}\s*.*:([\s\S]+?)(?=^{}(?:class|def)|\Z)'.format(class_indent, class_name, class_indent), content, flags=re.MULTILINE)
        if class_content and class_content.group(1):
            for function_name, function_args in functions:
                section_content = re.search(r'^\s*def\s+{}\s*\({}\)\s*:([\s\S]+?)(?=^\s*def)'.format(function_name, re.escape(function_args)), class_content.group(1), flags=re.MULTILINE)
                if section_content:
                    section_title_base = f"{file_name} - {class_name} - {function_name}"
                    cleaned_content = clean_string(section_content.group(1).strip())
                    split_contents = split_section_content(cleaned_content)

                    if len(split_contents) == 1:
                        sections[section_title_base] = split_contents[0]
                    else:
                        for i, part in enumerate(split_contents):
                            section_title = f"{section_title_base} (Part {i + 1})"
                            sections[section_title] = part

    return sections


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    sections = {}

    if file_path.endswith((".py")):
        sections = process_python_file(file_path)
        

        
    return {
        "file": file_path,
        "sections": sections
        # sections
    }

def process_directory(root_path):
    sections = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith((".py")):
                print(filename)
                file_path = os.path.join(dirpath, filename)
                sections.append(process_file(file_path))
    return sections


if __name__ == "__main__":
    repo_path = "/home/cfoye/Personal/podpac/podpac/"
    sections = process_directory(repo_path)
    print(sections)

    with open("code/code_output_sections.json", "w") as f:
        json.dump(sections, f, indent=4)