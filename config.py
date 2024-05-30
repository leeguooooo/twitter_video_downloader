# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')

class Config:
    STORAGE_DIR = STORAGE_DIR
