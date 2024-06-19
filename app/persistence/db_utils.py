from sqlmodel import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
PREFIX = os.getenv('PREFIX')

def get_engine():

  db_url = f'{PREFIX}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
  engine = create_engine(db_url, echo = True)
  
  return engine