from concurrent.futures import ThreadPoolExecutor
from flask import request, jsonify, render_template, Response, send_from_directory, abort
from flask_jwt_extended import jwt_required, create_access_token
from app import app
from app.utils import load_config, save_config, load_url_map, save_url_map, normalize_title, safe_join
from app.download import download_video_from_twitter, clients
import json
import os
import time
from urllib.parse import unquote
import requests

DOCKER_USERNAME = os.getenv('DOCKER_USERNAME')
DOCKER_PASSWORD = os.getenv('DOCKER_PASSWORD')

connections = []  # 全局连接列表
executor = ThreadPoolExecutor(max_workers=10)  # 线程池，限制最大线程数

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == DOCKER_USERNAME and password == DOCKER_PASSWORD:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/config', methods=['GET', 'POST'])
@jwt_required()
def config():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        save_config({"username": username, "password": password})
        return jsonify({"success": True}), 200
    else:
        config = load_config()
        config.pop('password', None)  # 不返回密码
        return jsonify(config), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_twitter_video():
    data = request.json
    twitter_url = data.get('url')

    if not twitter_url:
        return jsonify({"error": "No URL provided"}), 400

    # # 加载URL映射
    # url_map = load_url_map()
    # if (video_path := url_map.get(twitter_url)) is not None:
    #     return jsonify({"success": True, "message": "Video already downloaded", "video_path": video_path}), 200

    # # 初始化客户端的下载状态
    # client = {'progress': 0, 'status': 'downloading', 'downloaded': 0, 'total_size': 0, 'video_path': None}
    # clients.append(client)

    # # 启动后台线程进行下载
    # executor.submit(download_video_from_twitter, twitter_url, client, 1, True)  # 使用新的下载方法

    # return jsonify({"success": True, "message": "Download started"}), 200
    data, success = download_video_with_retry(twitter_url)
    if success:
        client = {'progress': 0, 'status': 'downloading', 'downloaded': 0, 'total_size': 0, 'video_path': None}
        clients.append(client)
        executor.submit(download_video_from_twitter, twitter_url, client, 1, True, data)  # 使用新的下载方法
        return jsonify({"success": True, "data": data}), 200
    else:
        return jsonify({"success": False, "message": data.get("msg", "Unknown error")}), 400

@app.route('/progress')
def progress():
    def generate():
        yield "data: Hello, world!\n\n"
        # connection = {}
        # connections.append(connection)  # 添加连接到全局列表

        # try:
        #     while True:
        #         if clients:
        #             app.logger.debug(f"Number of clients: {len(clients)}")
        #             app.logger.debug(f"Current client data: {clients[-1]}")
        #             try:
        #                 data = json.dumps(clients[-1])
        #                 app.logger.debug(f"Data to send: {data}")
        #                 yield f"data: {data}\n\n"
        #             except Exception as e:
        #                 app.logger.error(f"Error sending progress update: {e}")
        #                 break
        #         else:
        #             app.logger.debug("No clients connected.")
        #             data = json.dumps({"status": "waiting"})
        #             yield f"data: {data}\n\n"
        #             break
        #         time.sleep(2)
        # except GeneratorExit:
        #     app.logger.info("SSE client disconnected.")
        #     clients.pop(-1)
        # finally:
        #     connections.remove(connection)  # 从全局列表中移除连接

    return Response(generate(), mimetype='text/event-stream')

@app.route('/logs')
def stream_logs():
    def generate():
        connection = {}
        connections.append(connection)  # 添加连接到全局列表

        try:
            while True:
                yield "data: Hello, world!\n\n"
                time.sleep(1)
        except GeneratorExit:
            app.logger.info("SSE client disconnected.")
        finally:
            connections.remove(connection)  # 从全局列表中移除连接

    return Response(generate(), mimetype='text/event-stream')

@app.route('/files/<path:filename>')
def download_file(filename):
    # 对文件名进行解码
    filename = unquote(filename)
    try:
        safe_path = safe_join(app.config['STORAGE_DIR'], filename)
    except ValueError:
        abort(400, description="Invalid file path")
    if not os.path.exists(safe_path):
        app.logger.error(f"File not found: {safe_path}")
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(app.config['STORAGE_DIR'], filename)

@app.route('/url_map', methods=['GET'])
@jwt_required()
def get_url_map():
    url_map = load_url_map()
    processed_url_map = process_url_map(url_map)
    return jsonify(processed_url_map), 200

def process_url_map(url_map):
    new_url_map = {}
    for original_url, description in url_map.items():
        try:
            app.logger.debug(f"Processing URL: {original_url}")
            app.logger.debug(f"Description: {description}")

            if '__' not in description or '.' not in description:
                app.logger.debug(f"Skipping URL: {original_url}, invalid format in description")
                continue

            base_description, suffix = description.rsplit('__', 1)
            app.logger.debug(f"Base description: {base_description}, suffix: {suffix}")

            # 检查后缀是否是 n_n.mp4 类型
            if '_' in suffix and suffix.split('.')[0].split('_')[0].isdigit():
                n = int(suffix.split('.')[0].split('_')[0])
                base_url = original_url.rsplit('?', 1)[0]  # 去掉查询参数部分
                app.logger.debug(f"Base URL: {base_url}")

                # 生成 n 到 1 的后缀
                for i in range(n, 0, -1):
                    new_suffix = f"{i}_{i}.mp4"
                    new_description = f"{base_description}__{new_suffix}"
                    new_url = f"{base_url}?s=46&t=8Ea34CnZJICqgis5-jdwDA"  # 加上原有的查询参数部分
                    unique_key = f"{new_url}_{new_suffix}"  # 创建唯一键
                    new_url_map[unique_key] = new_description
                    app.logger.debug(f"Generated new URL: {new_url} with description: {new_description}")
            else:
                new_url_map[original_url] = description
                app.logger.debug(f"Added original URL: {original_url} with description: {description}")

        except Exception as e:
            app.logger.error(f"Error processing URL {original_url}: {e}")

    app.logger.debug(f"Final new URL map: {new_url_map}")
    return new_url_map

@app.route('/disconnect', methods=['POST'])
def disconnect():
    message = request.json.get('message')
    app.logger.info(f"Client disconnected: {message}")

    for connection in connections:
        connection.pop('active', None)  # 断开连接标记

    connections.clear()

    return jsonify({"success": True}), 200


def get_init_user():
    response = requests.get("http://xvideoget.com/twitter/initUser")
    if response.status_code == 200:
        result = response.json()
        data = result.get("data")
        # 保持 data 到 config.json
        config = load_config()
        config['uid'] = data  # 在 config 新增 uid: data
        save_config(config)
        return data
    return None


@app.route('/initUser', methods=['GET'])
def init_user():
    data = get_init_user()
    if data:
        return jsonify({"success": True, "data": data}), 200
    else:
        return jsonify({"success": False}), 400

def download_video_with_retry(url):
    config = load_config()

    uid = config.get('uid')
    if not uid:
        uid = get_init_user()

    # 构建请求数据
    request_data = {"videoUrl": url, "version": 202, "uid": uid}

    app.logger.info(f"getInfo video with URL: {url} and UID: {config.get('uid')}")
    # 打印 curl 命令
    curl_command = f"curl -X POST http://xvideoget.com/twitter/resolutionVideo -H 'Content-Type: application/x-www-form-urlencoded' -d '{'&'.join([f'{k}={v}' for k, v in request_data.items()])}'"
    print("Curl command for debugging:", curl_command)

    # 发送表单数据
    response = requests.post("http://xvideoget.com/twitter/resolutionVideo", data=request_data)

    if response.status_code == 200:
        result = response.json()
        app.logger.info(f"Response: {result}")
        if result.get("code") == 300:
            app.logger.info("UID expired, reinitializing user.")
            uid = get_init_user()
            if uid:
                # 更新请求数据
                request_data = {"videoUrl": url, "version": 202, "uid": uid}

                # 打印 curl 命令
                curl_command = f"curl -X POST http://xvideoget.com/twitter/resolutionVideo -H 'Content-Type: application/x-www-form-urlencoded' -d '{'&'.join([f'{k}={v}' for k, v in request_data.items()])}'"
                print("Curl command for debugging:", curl_command)

                # 发送表单数据
                response = requests.post("http://xvideoget.com/twitter/resolutionVideo", data=request_data)
                if response.status_code == 200 and response.json().get("data"):
                    return response.json(), True
        elif result.get("data"):
            return result, True
    return response.json(), False

@app.route('/resolutionVideo', methods=['GET'])
def get_resolution_video():
    url = request.args.get('url')
    data, success = download_video_with_retry(url)
    if success:
        client = {'progress': 0, 'status': 'downloading', 'downloaded': 0, 'total_size': 0, 'video_path': None}
        clients.append(client)
        executor.submit(download_video_from_twitter, url, client, 1, True, data)  # 使用新的下载方法
        return jsonify({"success": True, "data": data}), 200
    else:
        return jsonify({"success": False, "message": data.get("msg", "Unknown error")}), 400
