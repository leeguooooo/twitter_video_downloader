# Flask Application with Hot Reloading

This project is a Flask-based application with hot reloading capabilities. The application includes routes for authentication, configuration management, and video download from Twitter. It also provides real-time progress updates via SSE and log streaming.

## Project Structure

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

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following content:
   ```env
   JWT_SECRET_KEY=your_secret_key
   DOCKER_USERNAME=your_docker_username
   DOCKER_PASSWORD=your_docker_password
   ```

4. Run the application with hot reloading:
   ```bash
   python run.py
   ```

## Usage

### Authentication

- **Login**
  ```http
  POST /login
  {
      "username": "your_username",
      "password": "your_password"
  }
  ```

### Configuration Management

- **Get Configuration**
  ```http
  GET /config
  ```

- **Update Configuration**
  ```http
  POST /config
  {
      "username": "new_username",
      "password": "new_password"
  }
  ```

### Video Download

- **Download Video**
  ```http
  POST /download
  {
      "url": "twitter_video_url"
  }
  ```

- **Get Download Progress**
  ```http
  GET /progress
  ```

### Log Streaming

- **Stream Logs**
  ```http
  GET /logs
  ```

### Project Details

- **app/**: Contains the main application modules and functionalities.
- **logs/**: Stores application log files.
- **downloads/**: Directory for storing downloaded videos.
- **.env**: Environment variables for sensitive information.
- **config.json**: Configuration file for storing user credentials.
- **url_map.json**: Stores the mapping between Twitter URLs and downloaded video paths.
- **run.py**: Entry point for running the application with hot reloading.

### License

This project is licensed under the MIT License.
