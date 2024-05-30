from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sock import Sock
import os
from dotenv import load_dotenv
from config import Config


load_dotenv()

app = Flask(__name__)
sock = Sock(app)
app.config.from_object(Config)


# 配置JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')  # 请使用安全的密钥
jwt = JWTManager(app)

# 确保存储目录存在
if not os.path.exists(app.config['STORAGE_DIR']):
    os.makedirs(app.config['STORAGE_DIR'])

# 导入路由
from app.routes import *
from app.logging_config import setup_logging

setup_logging(app)
