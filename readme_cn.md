
# Flask 应用程序带热重载

此项目是一个基于 Flask 的应用程序，具有热重载功能。该应用程序包括身份验证、配置管理和从 Twitter 下载视频的路由。它还通过 SSE 提供实时进度更新和日志流。

## 项目结构

```
your_project/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── download.py
│   ├── utils.py
│   ├── config.py
│   ├── jwt.py
│   └── logging_config.py
│
├── logs/
│   └── app.log
│
├── downloads/
│
├── .env
├── config.json
├── url_map.json
└── run.py
```

## 开始

### 先决条件

- Python 3.7 或更高版本
- pip（Python 包管理器）

### 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

2. 安装所需软件包：
   ```bash
   pip install -r requirements.txt
   ```

3. 在根目录中创建 `.env` 文件，内容如下：
   ```env
   JWT_SECRET_KEY=your_secret_key
   DOCKER_USERNAME=your_docker_username
   DOCKER_PASSWORD=your_docker_password
   ```

4. 使用热重载运行应用程序：
   ```bash
   python run.py
   ```

## 用法

### 身份验证

- **登录**
  ```http
  POST /login
  {
      "username": "your_username",
      "password": "your_password"
  }
  ```

### 配置管理

- **获取配置**
  ```http
  GET /config
  ```

- **更新配置**
  ```http
  POST /config
  {
      "username": "new_username",
      "password": "new_password"
  }
  ```

### 视频下载

- **下载视频**
  ```http
  POST /download
  {
      "url": "twitter_video_url"
  }
  ```

- **获取下载进度**
  ```http
  GET /progress
  ```

### 日志流

- **流式日志**
  ```http
  GET /logs
  ```

### 项目详情

- **app/**：包含主要应用模块和功能。
- **logs/**：存储应用日志文件。
- **downloads/**：存储下载的视频的目录。
- **.env**：存储敏感信息的环境变量。
- **config.json**：存储用户凭证的配置文件。
- **url_map.json**：存储 Twitter URL 和下载视频路径的映射。
- **run.py**：使用热重载运行应用程序的入口点。

### 许可证

该项目根据 MIT 许可证授权。

# Apple Shortcut for Downloading Twitter Videos

To create an Apple Shortcut to check the clipboard and download a video:

1. Open the Shortcuts app on your iPhone or Mac.
2. Create a new shortcut.
3. Add the following actions:

   - **Get Clipboard**
   - **If**: `If [Clipboard] does not contain "x.com"`
     - **Show Alert**: "Clipboard does not contain a Twitter URL"
   - **Otherwise**:
     - **Get Contents of URL**:
       - URL: `https://yourserver.com/download`
       - Method: POST
       - Request Body: JSON
       - JSON: `{ "url": "[Clipboard]" }`
     - **Show Result**

4. Save the shortcut and give it a name like "Download Twitter Video".

Now, whenever you copy a Twitter URL to your clipboard and run this shortcut, it will send the URL to your Flask application and start the download process.
