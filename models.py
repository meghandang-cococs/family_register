from database import Base
from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey, SmallInteger, DateTime, Text
from datetime import datetime

class Family(Base):
    __tablename__ = "families"

    family_id = Column(Integer, primary_key=True)
    o_family_id = Column(String(15), nullable = False)
    password = Column(String(20), nullable=False)

    father_fname = Column(String(20), nullable=False)
    father_lname = Column(String(20), nullable=False)
    mother_fname = Column(String(20), nullable=False)
    mother_lname = Column(String(20), nullable=False)

    father_cname = Column(String(40), nullable=False)
    mother_cname = Column(String(40), nullable=False)

    address = Column(String(100), nullable=False)
    address2 = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    zip = Column(String(20), nullable=False)
    country = Column(String(2), nullable=False)

    email = Column(String(50), nullable=False)
    email2 = Column(String(50), nullable=False)

    phone = Column(String(20), nullable=False)
    phone2 = Column(String(20), nullable=False)

    created = Column(DateTime, nullable=False)
    modified = Column(DateTime, nullable=False)

    education = Column(SmallInteger, nullable=False)
    income = Column(SmallInteger, nullable=False)

    main_lang_id = Column(String(2), nullable=False)

    verified = Column(Boolean, nullable=False)
    activationCode = Column(String(6), nullable=False)

    status = Column(Boolean, nullable=False)
    level = Column(Boolean, nullable=False, default=False)

    help_id = Column(Integer, nullable=False)
    directory = Column(Boolean, nullable=False)

    ecp_name = Column(String(40), nullable=False)
    ecp_relation = Column(String(20), nullable=False)
    ecp_phone = Column(String(15), nullable=False)

    type = Column(SmallInteger, nullable=False)

    medical_cond = Column(String(200), nullable=False)
    allergy = Column(Integer, nullable=False)

    doctor_name = Column(String(40), nullable=False)
    doctor_phone = Column(String(15), nullable=False)

    ins_company = Column(String(40), nullable=False)
    ins_policy = Column(String(40), nullable=False)

    referral = Column(String(80), nullable=False, default=" ")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True)
    o_student_id = Column(String(20), nullable=False)

    family_id = Column(Integer, ForeignKey("families.family_id"), nullable=False)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(20), nullable=False)
    chinese_name = Column(String(256), nullable=False)

    dob = Column(String(20), nullable=False)     # stored as varchar in DB
    gender = Column(String(1), nullable=False)
    grade = Column(String(10), nullable=False)

    created = Column(DateTime, nullable=False)
    modified = Column(DateTime, nullable=False)

    status = Column(SmallInteger, nullable=False)

    email = Column(String(256), nullable=False)

    medical_cond = Column(String(40), nullable=False)
    allergy = Column(String(40), nullable=False)

    doctor_name = Column(String(40), nullable=False)
    doctor_phone = Column(String(20), nullable=False)

    ins_company = Column(String(40), nullable=False)
    ins_policy = Column(String(40), nullable=False)

class Classes(Base):
    __tablename__ = "classes"
    class_id = Column(Integer, primary_key=True, index=True)

    class_code = Column(String(10), nullable=False)
    category = Column(String(10), nullable=False)

    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    chinese_title = Column(String(100), nullable=False)
    chinese_description = Column(String(100), nullable=False)

    age = Column(SmallInteger, nullable=False)

    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    seats_x = Column(SmallInteger, nullable=False)
    weight = Column(Integer, nullable=False)

class CurrentClasses(Base):
    __tablename__ = "current_classes"

    year = Column(Integer)
    class_id = Column(Integer, primary_key=True) 

    category = Column(String(10))
    weight = Column(Integer)

    title = Column(String(100))
    description = Column(Text)             
    chinese_title = Column(String(100))
    chinese_description = Column(String(100))

class StudentClass(Base):
    __tablename__ = "student_class"

    sc_id = Column(Integer, primary_key=True)

    year = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    class_id = Column(Integer, nullable=False)

    wait = Column(Boolean, nullable=False)        
    paid = Column(Boolean, nullable=False)        

    paid_price = Column(Integer, nullable=True)

    created = Column(DateTime, nullable=False)
    removed = Column(DateTime, nullable=False)

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)

    family_id = Column(Integer, ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False,index=True)

    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    paid = Column(DateTime, nullable=True)
    canceled = Column(DateTime, nullable=True)

    amount = Column(Numeric(10, 2), nullable=False)

    payment_method = Column(String(15), nullable=False)
    transaction_id = Column(String(30), nullable=False)


class OrderStudentClass(Base):
    __tablename__ = "order_student_class"

    osc_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer,default=None)
    sc_id = Column(Integer,default=None)


class VolunteerActivities(Base):
    __tablename__ = "volunteer_activities"

    volunteer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    chinese_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False)
    persons = Column(Integer, nullable=False)


class VolunteerActivityYear(Base):
    __tablename__ = "volunteer_activity_year"

    vay_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)

    volunteer_id = Column(Integer, ForeignKey("volunteer_activities.volunteer_id"), nullable=False, index=True)

    persons = Column(Integer, nullable=False)    