import os
from os.path import dirname, join
from dotenv import load_dotenv

env_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL')
DATABASE_URL = os.getenv('DATABASE_URL')