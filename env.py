import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name):
    return os.getenv(name)

APP_SERVER_URL = get_env('APP_SERVER_URL')
PORT = get_env('PORT')