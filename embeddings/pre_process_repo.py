import os
import re
import json

def extract_comments(file_content):
    single_line_comments = re.findall(r"//.*", file_content)
    multi_line_comments = re.findall(r"/\*[\s\S]*?\*/", file_content)
    return single_line_comments + multi_line_comments

def extract_docstrings(file_content):
    docstrings = re.findall(r'""".*?"""', file_content, re.DOTALL)
    return docstrings

def extract_python_sections(file_content):
    # Define regex patterns for classes and functions
    class_pattern = r"(class\s+\w+\s*(?:\([^\)]*\))?\s*:\s*(?:(?:(?:\n(?:\t| {4})).+)+)?)"
    function_pattern = r"(def\s+\w+\s*\([^\)]*\)\s*:\s*(?:(?:(?:\n(?:\t| {4})).+)+)?)"

    # Combine the patterns
    pattern = r"|".join([class_pattern, function_pattern])

    # Find the start indices of matched sections
    start_indices = [m.start() for m in re.finditer(pattern, file_content)]

    # Find the end indices of matched sections by checking the indentation level
    end_indices = []
    for i, start_index in enumerate(start_indices[:-1]):
        for line in file_content[start_indices[i+1]:].split("\n"):
            if not re.match(r"\s*\S", line):
                end_indices.append(start_indices[i+1] + line.rfind("\n"))
                break
        else:
            end_indices.append(len(file_content))
    end_indices.append(len(file_content))

    sections = [file_content[start:end].strip() for start, end in zip(start_indices, end_indices)]

    return sections
def extract_related_sections(file_content):
    # Assuming the code is written in Python, adjust the function for other languages
    return extract_python_sections(file_content)

def extract_code_snippets(file_content):
    code_snippets = re.split(r'//.*|/\*[\s\S]*?\*/|""".*?"""', file_content, re.DOTALL)
    
    related_sections = []
    for snippet in code_snippets:
        related_sections.extend(extract_related_sections(snippet))
    
    return related_sections



def process_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    comments = extract_comments(content)
    docstrings = extract_docstrings(content)
    code_snippets = extract_code_snippets(content)

    return {
        "file": file_path,
        "comments": comments,
        "docstrings": docstrings,
        "code_snippets": code_snippets,
    }

def process_directory(root_path):
    sections = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith((".py", ".js", ".java", ".c", ".cpp", ".h", ".hpp")):
                file_path = os.path.join(dirpath, filename)
                sections.append(process_file(file_path))
    return sections

if __name__ == "__main__":
    repo_path = "/home/cfoye/podpac/podpac/core/compositor/test"
    sections = process_directory(repo_path)

    with open("small_output_sections.json", "w") as f:
        json.dump(sections, f, indent=4)
