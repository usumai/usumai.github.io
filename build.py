import os
import json
import fnmatch
import re

def extract_doc_info(content):
    title_pattern = r'let doc_title = "(.*?)"'
    order_pattern = r'let doc_order = (\d+)'
    id_pattern = r'let doc_id = (\d+)'
    
    doc_title_match = re.search(title_pattern, content)
    doc_order_match = re.search(order_pattern, content)
    doc_id_match = re.search(id_pattern, content)
    
    doc_title = doc_title_match.group(1) if doc_title_match else None
    doc_order = int(doc_order_match.group(1)) if doc_order_match else None
    doc_id = int(doc_id_match.group(1)) if doc_id_match else None
    
    return {"doc_title": doc_title, "doc_order": doc_order, "doc_id": doc_id}

def insert_into_structure(structure, path_parts, file, doc_info):
    for part in path_parts:
        structure = structure.setdefault(part, {})
    structure[file] = doc_info

def build_tree(start_path, ignore_patterns=None, ignore_regex=None):
    structure = {}
    for root, dirs, files in os.walk(start_path):
        
        # Remove dirs/files that match the ignore patterns
        if ignore_patterns:
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in ignore_patterns)]
            files = [f for f in files if not any(fnmatch.fnmatch(f, pattern) for pattern in ignore_patterns)]
        
        # Remove dirs/files that match the ignore regex
        if ignore_regex:
            dirs[:] = [d for d in dirs if not ignore_regex.match(d)]
            files = [f for f in files if not ignore_regex.match(f)]
        
        # Extract doc info and store in the structure dictionary
        for file in files:
            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            doc_info = extract_doc_info(content)
            relative_path = os.path.relpath(os.path.join(root, file), start_path)
            doc_info["path"] = relative_path.replace("\\", "/")  # Convert Windows paths to web-friendly format
            path_parts = relative_path.split(os.sep)[:-1]  # Exclude the file itself
            insert_into_structure(structure, path_parts, file, doc_info)

    return structure

directory_path = './docs/'  # Current directory

# List of patterns to ignore
ignore_patterns = ['*.tmp', 'backup', '.git', '__pycache__', 'pasgetisite', '*.git', 'structure.json', 'index.html', 'build.py']

# Regular expression to ignore certain patterns (e.g., all files/folders starting with 'test')
ignore_regex = re.compile(r'^test.*')

tree_structure = build_tree(directory_path, ignore_patterns, ignore_regex)

# Save the structure to a JS file named "structure.js"
with open('structure.js', 'w') as js_file:
    js_file.write("export const jsonData = ")
    json.dump(tree_structure, js_file, indent=4)
