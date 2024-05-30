import os
import json
import re

def load_config():
    if not os.path.exists('config.json'):
        return {"username": "", "password": ""}
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def load_url_map():
    if not os.path.exists('url_map.json'):
        return {}
    with open('url_map.json', 'r') as f:
        return json.load(f)

def save_url_map(url_map):
    with open('url_map.json', 'w') as f:
        json.dump(url_map, f)

def safe_join(directory, path):
    # 确保路径安全
    base_directory = os.path.abspath(directory)
    full_path = os.path.abspath(os.path.join(directory, path))
    if not full_path.startswith(base_directory):
        raise ValueError("Attempted path traversal attack")
    return full_path

def normalize_title(title):
    # 只保留数字、中文和英文字符，其他字符替换为下划线
    return re.sub(r'[^\w\u4e00-\u9fff]', '_', title)
