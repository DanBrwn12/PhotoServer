import os
from dotenv import load_dotenv

# Загружаем .env в переменные окружения
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY")
PHOTOS_PATH = os.environ.get("PHOTOS_PATH", os.path.join(BASE_DIR, "photos"))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")