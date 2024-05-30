import os
import json
import re
import subprocess
import time
from app.utils import load_config, save_url_map, load_url_map, normalize_title
from app import app
import requests

clients = []

def download_video_from_twitter(url, client, max_retries=1, use_new_method=False, video_info=None):
    if use_new_method:
        download_video_new_method(url, client, max_retries, video_info)
    else:
        download_video_old_method(url, client, max_retries)

def download_video_old_method(url, client, max_retries=1):
    config = load_config()
    username = config.get('username')
    password = config.get('password')

    app.logger.info(f"Username: {username}")
    # app.logger.info(f"Password: {password}")

    if not username or not password:
        raise Exception("Twitter credentials are not set")

    # 获取推特内容信息
    info_cmd = ['yt-dlp', '--username', username, '--password', password, '--no-check-certificate', '--dump-json', url]

    for attempt in range(max_retries):
        info_result = subprocess.run(info_cmd, capture_output=True, text=True)
        if info_result.returncode == 0:
            break
        else:
            app.logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {info_result.stderr}")
            time.sleep(2)  # 等待一段时间再重试
    else:
        error_message = f"Error retrieving video info after {max_retries} attempts: {info_result.stderr}"
        app.logger.error(error_message)
        client['status'] = 'error'
        client['error_message'] = error_message
        return

    raw_output = info_result.stdout
    app.logger.info(f"yt-dlp command: {' '.join(info_cmd)}")
    app.logger.info(f"yt-dlp raw output: {raw_output}")

    # 使用正则表达式拆分多个 JSON 对象
    json_objects = re.findall(r'\{.*?\}(?=\s*\{|\s*$)', raw_output)

    for idx, json_str in enumerate(json_objects, start=1):
        try:
            video_info = json.loads(json_str)
        except json.JSONDecodeError as e:
            app.logger.error(f"Error decoding JSON: {e}")
            client['status'] = 'error'
            client['error_message'] = f"Error decoding JSON: {e}"
            return

        video_title = normalize_title(video_info.get('title', f'downloaded_video_{idx}'))
        output_template = os.path.join(app.config['STORAGE_DIR'], f"{video_title}_{idx}.%(ext)s")

        # 检查视频是否已存在
        video_path = output_template % {'ext': 'mp4'}
        if os.path.exists(video_path):
            client['status'] = 'completed'
            client['video_path'] = os.path.basename(video_path)
            continue

        cmd = ['yt-dlp', '--username', username, '--password', password, '--no-check-certificate', '-o', output_template, url]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            app.logger.info(line.strip())
            if "[download]" in line:
                progress = extract_progress(line)
                if progress is not None:
                    client['progress'] = progress['progress']
                    client['downloaded'] = progress['downloaded']
                    client['total_size'] = progress['total_size']

        process.wait()

        stderr_output = process.stderr.read()
        if process.returncode != 0:
            error_message = f"Error downloading video: {stderr_output}"
            client['status'] = 'error'
            client['error_message'] = error_message
            app.logger.error(error_message)
            return
        else:
            client['status'] = 'completed'
            client['video_path'] = os.path.basename(video_path)

            # 更新 URL 和文件映射关系
            url_map = load_url_map()
            url_map[url] = client['video_path']
            save_url_map(url_map)

def download_video_new_method(url, client, max_retries=1, video_info=None):
    response = video_info

    videos = response.get('data', {}).get('videos', [])
    if not videos:
        error_message = "No videos found in response"
        app.logger.error(error_message)
        client['status'] = 'error'
        client['error_message'] = error_message
        return

    url_map = load_url_map()

    for idx, video_info in enumerate(videos, start=1):
        video_url = video_info.get('url')
        video_title = normalize_title(video_info.get('title', f'downloaded_video_{idx}'))
        output_template = os.path.join(app.config['STORAGE_DIR'], f"{video_title}_{idx}.%(ext)s")

        # 检查视频是否已存在
        video_path = output_template % {'ext': 'mp4'}
        if os.path.exists(video_path):
            client['status'] = 'completed'
            client['video_path'] = os.path.basename(video_path)
            app.logger.info(f"Video already exists: {video_path}")
            continue

        cmd = ['yt-dlp', '-o', output_template, video_url]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            app.logger.info(line.strip())
            if "[download]" in line:
                progress = extract_progress(line)
                if progress is not None:
                    client['progress'] = progress['progress']
                    client['downloaded'] = progress['downloaded']
                    client['total_size'] = progress['total_size']
                    app.logger.info(f"Download progress: {progress['progress']}%")

        process.wait()

        stderr_output = process.stderr.read()
        if process.returncode != 0:
            error_message = f"Error downloading video: {stderr_output}"
            client['status'] = 'error'
            client['error_message'] = error_message
            app.logger.error(error_message)
            return
        else:
            client['status'] = 'completed'
            client['video_path'] = os.path.basename(video_path)
            app.logger.info(f"Video downloaded successfully: {video_path}")

            # 更新 URL 和文件映射关系
            unique_key = f"{url}_{idx}"
            url_map[unique_key] = client['video_path']
            save_url_map(url_map)
            app.logger.info(f"URL and file mapping updated: {url} -> {client['video_path']}")

def extract_progress(line):
    # 解析 yt-dlp 输出，提取进度信息
    match = re.search(r'\[download\]\s+([\d\.]+)%\s+of\s+~?\s*([\d\.]+)([KMG]iB)', line)
    if match:
        progress = float(match.group(1))
        downloaded = float(match.group(2))
        unit = match.group(3)
        total_size = convert_to_bytes(downloaded, unit)
        return {'progress': progress, 'downloaded': downloaded, 'total_size': total_size}
    return None

def convert_to_bytes(size, unit):
    units = {'KiB': 1024, 'MiB': 1024**2, 'GiB': 1024**3}
    return size * units.get(unit, 1)
