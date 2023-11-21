import os
import re
import shutil
import json 

def clean_name(name):
    # Regular expression to find the random string pattern followed by a file extension or at the end
    pattern = re.compile(' \w{32}(?=\.\w+|$|(?=_all))')
    match = pattern.search(name)
    # Remove the pattern if found and return the cleaned name
    if match:
        cleaned_name = re.sub(pattern, '', name).strip('')
        matched_str = name[match.span()[0]:match.span()[1]].strip('_all')
        return cleaned_name, matched_str
    else: 
        print(f"no match found for {name}")
        return name, None 

def _rename(root, d):
    for file in os.listdir(root):
        clean_file_name, matched_str = clean_name(file)
        if clean_file_name != file:
            original_file_path = os.path.join(root, file)
            new_file_path = os.path.join(root, clean_file_name)
            print(f'Renaming file: {original_file_path} to {new_file_path}')
            d[clean_file_name] = matched_str
            shutil.move(original_file_path, new_file_path)

def rename(root, d):
    _rename(root, d)
    for item in os.listdir(root):
        item_path = os.path.join(root, item)

        if os.path.isdir(item_path):
            rename(item_path, d)

if __name__ == '__main__':
    d = {}
    data_dir = "data"

    rename(data_dir, d)

    # save directory name file to data directory 
    with open(os.path.join(data_dir, "directory_name.json"), 'w') as json_file:
        json.dump(d, json_file)