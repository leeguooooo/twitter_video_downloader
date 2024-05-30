import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    # 配置日志记录
    LOG_DIR = 'logs'
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 配置日志轮转，最大文件大小为10MB，保留3个备份文件
    log_file = os.path.join(LOG_DIR, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=1 * 1024 * 1024, backupCount=3)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # 配置控制台日志处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)

    # 清除 Flask 默认的处理器，添加自定义的处理器
    if not app.debug:
        app.logger.handlers = []
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)

    # 设置日志文件路径
    app.config['LOG_FILE'] = log_file
