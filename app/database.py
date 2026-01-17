"""
Filename: database.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Establishes connection to database
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

if os.environ.get('TESTING') == '1':
    DATABASE_URL = 'sqlite:///./test.db' 
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = 'mysql+pymysql://test' # connect database
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()
