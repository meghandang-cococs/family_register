from fastapi import APIRouter,HTTPException, status
from sqlalchemy import func, desc
from datetime import datetime
from pydantic import BaseModel, Field
from models import Family, Order, OrderStudentClass, StudentClass, Student, Classes, VolunteerActivities, VolunteerActivityYear
from .auth import db_dependency, family_dependency


router = APIRouter(
    prefix = '/family',
    tags = ['family']
)

class CreateFamilyRequest(BaseModel):
    email: str
    father_fname: str
    father_lname: str
    mother_fname: str
    mother_lname: str
    father_cname: str
    mother_cname: str
    address: str
    address2: str
    city: str
    state: str
    zip: str
    country: str
    email2: str
    phone: str
    phone2: str
    education: int
    income: int
    main_lang_id: str
    ecp_name: str
    ecp_relation: str
    ecp_phone: str
    medical_cond: str
    allergy: int
    doctor_name: str
    doctor_phone: str
    ins_company: str
    ins_policy: str


class NewPasswordCheck(BaseModel):
    password: str = Field(min_length=6, max_length=64)
    new_password: str = Field(min_length = 6, max_length=64)


@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def initial_family_signup(db: db_dependency, req: CreateFamilyRequest):
    if req.password != req.check_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    existing_profile = db.query(Family).filter(Family.email == req.email).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    now = datetime.utcnow()
    new_family = Family(
        email=req.email,
        password= req.password,
        o_family_id = "",
        father_fname="",
        father_lname="",
        mother_fname="",
        mother_lname="",
        father_cname="",
        mother_cname="",
        address="",
        address2="",
        city="",
        state="",
        zip="",
        country="US",
        email2="",
        phone="",
        phone2="",

        created=now,
        modified=now,

        education=0,
        income=0,
        main_lang_id="",

        verified=0,
        activationCode="000000",
        status=0,
        level=0,

        help_id=0,
        directory=0,

        ecp_name="",
        ecp_relation="",
        ecp_phone="",

        type=0,
        medical_cond="",
        allergy=0,
        doctor_name="",
        doctor_phone="",
        ins_company="",
        ins_policy="",

        referral=" "

    )

    db.add(new_family)
    db.commit()
    db.refresh(new_family)
    return {"family_id": new_family.family_id}


@router.get("/profile/view")
async def get_family(family: family_dependency, db: db_dependency):
    if family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return db.query(Family).filter(Family.family_id == family.get('family_id')).first()


@router.put("/profile/edit", status_code = status.HTTP_200_OK)
async def update_family_profile(db: db_dependency, family: family_dependency, profile_change: CreateFamilyRequest):
    if family is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    profile_model = db.query(Family).filter(Family.family_id == family.get('family_id')).first()
    if profile_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    profile_model.father_fname = profile_change.father_fname
    profile_model.father_lname = profile_change.father_lname
    profile_model.mother_fname = profile_change.mother_fname
    profile_model.mother_lname = profile_change.mother_lname
    profile_model.father_cname = profile_change.father_cname
    profile_model.mother_cname = profile_change.mother_cname
    profile_model.address = profile_change.address
    profile_model.address2 = profile_change.address2
    profile_model.city = profile_change.city
    profile_model.state = profile_change.state
    profile_model.zip = profile_change.zip
    profile_model.country = profile_change.country
    profile_model.email = profile_change.email
    profile_model.email2 = profile_change.email2
    profile_model.phone = profile_change.phone
    profile_model.phone2 = profile_change.phone2
    profile_model.education = profile_change.education
    profile_model.income = profile_change.income
    profile_model.main_lang_id = profile_change.main_lang_id
    profile_model.ecp_name = profile_change.ecp_name
    profile_model.ecp_relation = profile_change.ecp_relation
    profile_model.ecp_phone = profile_change.ecp_phone
    profile_model.medical_cond = profile_change.medical_cond
    profile_model.allergy = profile_change.allergy
    profile_model.doctor_name = profile_change.doctor_name
    profile_model.doctor_phone = profile_change.doctor_phone
    profile_model.ins_company = profile_change.ins_company
    profile_model.ins_policy = profile_change.ins_policy

    now = datetime.utcnow()
    profile_model.modified = now

    db.add(profile_model)
    db.commit()



''' Not needed anymore if not storing passwords
@router.put("/password/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(family: family_dependency, db: db_dependency,
                          new_password: NewPasswordCheck):
    if family is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    profile_model = db.query(Family).filter(Family.family_id == family.get('family_id')).first()

    if not bcrypt_context.verify(new_password.password, profile_model.password):
        raise HTTPException(status_code=401, detail='Error on password change')
    profile_model.password = bcrypt_context.hash(new_password.new_password)
    db.add(profile_model)
    db.commit()
''' 

# From payments.php lines 30-39, returns 10 fields, 5 of which are displayed by front-end
@router.get("/payments")
async def view_payments(db: db_dependency, family: family_dependency):
    order_query = (
        db.query(Order, func.count(OrderStudentClass.osc_id).label("number_of_classes"))
        .outerjoin(OrderStudentClass, Order.order_id == OrderStudentClass.order_id)
        .filter(Order.family_id == family.get('family_id'))
        .filter(Order.paid.isnot(False))   
        .group_by(Order.order_id)
        .order_by(Order.paid)
        .all()
    )

    return [
        {
            **{c.key: getattr(order, c.key) for c in order.__table__.columns},
            "number_of_classes": int(class_count),
        }
        for order, class_count in order_query
    ]

# From view_order.php lines 30-42, returns 16 fields, 9 of which are displayed by front-end
@router.get("/payments/view_order_details/{order_id}")
async def view_order(db: db_dependency, family: family_dependency, order_id: int):
    order_query = (
        db.query(Order, func.count(OrderStudentClass.osc_id).label('number_of_classes'), 
                Family.family_id, Family.father_fname, Family.father_lname, Family.mother_fname,
                Family.mother_lname, Family.father_cname, Family.mother_cname)
        .select_from(Order)
        .outerjoin(OrderStudentClass, OrderStudentClass.order_id == Order.order_id)
        .join(Family, Family.family_id == Order.family_id)
        .filter(Order.order_id == order_id)
        .filter(Order.family_id == family.get('family_id'))
        .filter(Order.paid.isnot(None))
        .group_by(Order.order_id)
        .first())

    if not order_query:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order, number_of_classes, fam_id, father_fname, father_lname, mother_fname, mother_lname, father_cname, mother_cname = order_query

    return {
        **{c.key: getattr(order, c.key) for c in order.__table__.columns},
        "number_of_classes": int(number_of_classes), "family_id": fam_id, "father_fname": father_fname,
        "father_lname": father_lname, "mother_fname": mother_fname, "mother_lname": mother_lname,
        "father_cname": father_cname, "mother_cname": mother_cname
    }



# from view_order.php lines 60-124, returns table with details on every class/product/volunteer/discount in the order
@router.get("/payments/view_order_classes/{order_id}")
async def view_order(db: db_dependency, family: family_dependency, order_id: int):
    order_query = (
        db.query(Order.created,
                Student.student_id, 
                Student.first_name, 
                Student.last_name, 
                Student.chinese_name, 
                StudentClass.class_id, 
                StudentClass.paid_price, 
                Classes.title, 
                Classes.chinese_title)
        .select_from(Order)
        .join(OrderStudentClass, (OrderStudentClass.order_id == Order.order_id))
        .join(StudentClass, StudentClass.sc_id == OrderStudentClass.sc_id)
        .outerjoin(Student, Student.student_id == StudentClass.student_id)
        .outerjoin(Classes, Classes.class_id == StudentClass.class_id)
        .filter(Order.order_id == order_id)
        .filter(Order.family_id == family.get('family_id'))
        .filter(Order.paid != 0)
        .order_by(desc(Student.dob), StudentClass.sc_id)
    )

    if not order_query:
        raise HTTPException(status_code=404, detail="No classes found for this order")

    results = order_query.all()

    # goes through every row, if it is a volunteer log (class_id == 0), then replaces row
    total = 0
    final_data = []
    for row in results:
    
        if row.student_id == None: 
            # get volunteer activity
            vol_query = (db.query(VolunteerActivities.name.label("title"))
                .join(
                    VolunteerActivityYear,
                    VolunteerActivityYear.volunteer_id == VolunteerActivities.volunteer_id
                )
                .filter(VolunteerActivityYear.volunteer_id == row.class_id)
                .first())    

            item = {
                "created": row.created,
                "student_id": row.student_id,
                "name": "Family",
                "chinese_name": row.chinese_name,
                "class_id": row.class_id,
                "paid_price": str(row.paid_price), # Convert Decimal to string for JSON if needed
                "title": vol_query.title,
                "chinese_title": row.chinese_title
            }

            final_data.append(item)
        else:
            item = {
                "created": row.created,
                "student_id": row.student_id,
                "first_name": row.first_name, 
                "last_name": row.last_name,
                "chinese_name": row.chinese_name,
                "class_id": row.class_id,
                "paid_price": str(row.paid_price), # Convert Decimal to string for JSON if needed
                "title": row.title,
                "chinese_title": row.chinese_title
            }
    
            final_data.append(item)

        total += row.paid_price

    # sibling discount   
    student_count = (
                db.query(func.count(func.distinct(StudentClass.student_id)))
                .join(OrderStudentClass, OrderStudentClass.sc_id == StudentClass.sc_id)
                .filter(OrderStudentClass.order_id == order_id)
                .filter(StudentClass.student_id > 0)
                .scalar()
            )
    
    if student_count > 1:
            discount = (student_count - 1) * -15
            total += discount 
            item = {
                "name": "Sibling Discount", 
                "paid_price": discount, # Convert Decimal to string for JSON if needed
            } 
            final_data.append(item)    

    # total 
    item = {"name": "Total", "Price": total}
    final_data.append(item)

    return final_data

