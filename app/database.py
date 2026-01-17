import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

if os.environ.get('TESTING') == '1':
    DATABASE_URL = 'sqlite:///./test.db'
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = 'mysql+pymysql://cococs:1234@127.0.0.1:3306/cococs'
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()


'''
{
  "email": "khuynh",
  "password": "dangdang",
  "check_password": "dangdang" 
}

{
  "email": "khuynh@e.com",
  "father_fname": "g",
  "father_lname": "d",
  "mother_fname": "k",
  "mother_lname": "h",
  "father_cname": "d",
  "mother_cname": "h",
  "address": "16",
  "address2": "",
  "city": "ac",
  "state": "ca",
  "zip": "94503",
  "country": "",
  "email2": "gdang@e.com",
  "phone": "7777777777",
  "phone2": "7777777777",
  "education": 0,
  "income": 0,
  "main_lang_id": "c",
  "ecp_name": "s",
  "ecp_relation": "a",
  "ecp_phone": "7777777777",
  "medical_cond": "",
  "allergy": 0,
  "doctor_name": "k",
  "doctor_phone": "7777777777",
  "ins_company": "k",
  "ins_policy": "7777777777"
}

{
  "first_name": "kaitlin",
  "last_name": "dang",
  "chinese_name": "string",
  "dob": "7/29/2002",
  "gender": "f",
  "grade": "8",
  "email": "kdang@e.com",
  "medical_cond": "",
  "allergy": "",
  "doctor_name": "k",
  "doctor_phone": "7777777777",
  "ins_company": "kp",
  "ins_policy": "7777777777"
}
'''


