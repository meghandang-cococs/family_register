"""
Filename: utils.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Utilities for unit testing. Overriding functions and creating testing models
"""

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from app.models import Classes, CurrentClasses, Family, FamilyYear, Student, StudentClass, Order, OrderStudentClass, VolunteerActivities, VolunteerActivityYear

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_family():
    return {'email': 'test1@e.com', 'family_id': 1}

client = TestClient(app)
now = datetime.utcnow()


@pytest.fixture
def test_classes():
    test_class = Classes(
        class_id = "1",
        class_code = "1",
        category = "LC",
        title = "Level 1",
        description = "This is Level 1",
        chinese_title = "东西",
        chinese_description = "东西",
        age = 0,
        created = now,
        modified = now,
        seats_x = 1,
        weight = 1
    )

    db = TestingSessionLocal()
    db.add(test_class)
    db.commit()
    yield test_class
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM classes;"))
        connection.commit()


@pytest.fixture
def test_current_classes_1():
    test_class_1 = CurrentClasses(
        year = now.year,
        class_id = "1",
        category = "LC",
        weight = 1,
        title = "Level 1",
        description = "This is Level 1",            
        chinese_title = "东西",
        chinese_description = "东西"
    )

    db = TestingSessionLocal()
    db.add(test_class_1)
    db.commit()
    yield test_class_1
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM current_classes;"))
        connection.commit()


@pytest.fixture
def test_current_classes_2():
    test_class_2 = CurrentClasses(
        year = now.year,
        class_id = "1",
        category = "LC",
        weight = 1,
        title = "Calligraphy",
        description = "This is Calligraphy",            
        chinese_title = "东西",
        chinese_description = "东西"
    )

    db = TestingSessionLocal()
    db.add(test_class_2)
    db.commit()
    yield test_class_2
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM current_classes;"))
        connection.commit()



@pytest.fixture
def test_family():
    family = Family(
        family_id="1",
        email = "test1@e.com",
        password = "1234",
        o_family_id = "",
        father_fname = "Father",
        father_lname = "Test",
        mother_fname = "Mother",
        mother_lname = "Test",
        father_cname = "爸",
        mother_cname = "妈",
        address = "",
        address2 = "",
        city = "",
        state = "",
        zip = "",
        country = "US",
        email2 = "",
        phone = "7777777777",
        phone2 = "",
        created = now,
        modified = now,
        education = 0,
        income = 0,
        main_lang_id = "",
        verified = 0,
        activationCode = "000000",
        status = 0,
        level = 0,
        help_id = 0,
        directory = 0,
        ecp_name = "",
        ecp_relation = "",
        ecp_phone = "",
        type = 0,
        medical_cond = "",
        allergy = 0,
        doctor_name = "",
        doctor_phone = "",
        ins_company = "",
        ins_policy = "",
        referral = " "
        
    )

    db = TestingSessionLocal()
    db.add(family)
    db.commit()
    yield family
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM families;"))
        connection.commit()


@pytest.fixture
def test_family_year():
    test_fam_year = FamilyYear(
        year = 2026,
        family_id = "1",
        paid = 1,
        vay_id = "1"
    )

    db = TestingSessionLocal()
    db.add(test_fam_year)
    db.commit()
    yield test_fam_year
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM family_year;"))
        connection.commit()  


@pytest.fixture
def test_student():
    test_student = Student(
        student_id = "1",
        o_student_id = "",
        family_id = "1",
        first_name = "Student",
        last_name = "Test",
        chinese_name = "同学",
        dob = "01/01/2000",
        gender = "M",
        grade = "0",
        created = now,
        modified = now,
        status = 1,
        email = "test@e.com",
        medical_cond = "Example",
        allergy = "Example",
        doctor_name = "Example",
        doctor_phone = "Example",
        ins_company = "Example",
        ins_policy = "Example"
    )

    db = TestingSessionLocal()
    db.add(test_student)
    db.commit()
    yield test_student
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM students;"))
        connection.commit() 


@pytest.fixture
def test_student_class_unpaid():
    test_student_class = StudentClass(
        year = 2026,
        student_id = 1,
        class_id = 1,
        wait = False,        
        paid = False,        
        paid_price = 0,
        created = now,
        removed = now
    )
    db = TestingSessionLocal()
    db.add(test_student_class)
    db.commit()
    yield test_student_class
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM student_class;"))
        connection.commit()

@pytest.fixture
def test_student_class_paid():
    test_student_class = StudentClass(
        year = 2026,
        student_id = 1,
        class_id = 1,
        wait = False,        
        paid = True,        
        paid_price = 0,
        created = now,
        removed = now
    )
    db = TestingSessionLocal()
    db.add(test_student_class)
    db.commit()
    yield test_student_class
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM student_class;"))
        connection.commit()

@pytest.fixture
def test_order():
    order = Order(
        year = 2026,
        family_id = 1,
        created = now,
        paid = None,
        canceled = None,
        amount = 1.00,
        payment_method = "card",
        transaction_id = "123456"
    )
    db = TestingSessionLocal()
    db.add(order)
    db.commit()
    db.refresh(order)
    yield order
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM orders;"))
        connection.commit()


@pytest.fixture
def test_order_paid():
    order = Order(
        year = 2026,
        family_id = 1,
        created = now,
        paid = now,
        canceled = None,
        amount = 1.00,
        payment_method = "card",
        transaction_id = "1234567"
    )
    db = TestingSessionLocal()
    db.add(order)
    db.commit()
    db.refresh(order)
    yield order
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM orders;"))
        connection.commit()


@pytest.fixture
def test_order_student_class():
    order_student_class = OrderStudentClass(
        osc_id = "1",
        order_id = "1",
        sc_id = "1",
    )

    db = TestingSessionLocal()
    db.add(order_student_class)
    db.commit()
    yield order_student_class
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM order_student_class;"))
        connection.commit()


@pytest.fixture
def test_voluneer_activity():
    volunteer = VolunteerActivities(
        volunteer_id = 1,
        name = "Some Activity",
        chinese_name = "东西",
        is_active = True,
        persons = 1
    )

    db = TestingSessionLocal()
    db.add(volunteer)
    db.commit()
    yield volunteer
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM volunteer_activities;"))
        connection.commit()


@pytest.fixture
def test_volunteer_activity_year():
    volunteer_activity_year = VolunteerActivityYear(
        vay_id = "1",
        year = 2026,
        volunteer_id = "1",
        persons = 1
    )

    db = TestingSessionLocal()
    db.add(volunteer_activity_year)
    db.commit()
    yield volunteer_activity_year
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM volunteer_activity_year;"))
        connection.commit()







