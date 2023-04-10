
import json
import re
import os

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Code to process .MD file:
    sections = {}
    section_titles = re.findall(r'^#{1,6} (.+)$', content, flags=re.MULTILINE)
    for title in section_titles:
        section_content = re.search(r'^#* {}(?:\n|\r\n)(.+?)(?:\n|\r\n)#'.format(re.escape(title)), content, flags=re.MULTILINE | re.DOTALL)
        if section_content:
            sections[title] = section_content.group(1).strip()
        
    return {
        "file": file_path,
        "sections": sections
        # sections
    }

def process_directory(root_path):
    sections = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith((".md")):
                print(filename)
                file_path = os.path.join(dirpath, filename)
                sections.append(process_file(file_path))
    return sections


if __name__ == "__main__":
    repo_path = "/home/cfoye/Personal/podpac/doc/source"
    sections = process_directory(repo_path)
    print(sections)

    with open("docs/doc_output_sections.json", "w") as f:
        json.dump(sections, f, indent=4)