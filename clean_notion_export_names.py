import os
import re
import shutil

def clean_name(name):
    # Regular expression to find the random string pattern followed by a file extension or at the end
    pattern = r' \w{32}(?=\.\w+|$)'
    # Remove the pattern if found and return the cleaned name
    return re.sub(pattern, '', name)

def _rename(root):
    for file in os.listdir(root):
        clean_file_name = clean_name(file)
        if clean_file_name != file:
            original_file_path = os.path.join(root, file)
            new_file_path = os.path.join(root, clean_file_name)
            print(f'Renaming file: {original_file_path} to {new_file_path}')
            shutil.move(original_file_path, new_file_path)

def rename(root):
    _rename(root)
    for item in os.listdir(root):
        item_path = os.path.join(root, item)

        if os.path.isdir(item_path):
            rename(item_path)

rename("data")