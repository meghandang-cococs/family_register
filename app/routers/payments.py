"""
Filename: payments.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Endpoints points handling Order viewing
"""

from fastapi import APIRouter,HTTPException, status
from datetime import datetime
from sqlalchemy import func, desc, and_
from ..models import Family, Order, OrderStudentClass, StudentClass, Student, Classes, VolunteerActivities, VolunteerActivityYear
from .auth import db_dependency, family_dependency


router = APIRouter(
    prefix = '/family',
    tags = ['payments']
)


# from checkout.php 53-72
@router.get("/checkout", status_code = status.HTTP_200_OK)
async def view_cart(db: db_dependency, family: family_dependency):
    current_year = datetime.now().year

    cart = (
        db.query(
            Family.verified.label("verified"),
            Student.first_name.label("first_name"),
            Student.last_name.label("last_name"),
            Student.chinese_name.label("chinese_name"),
            StudentClass,  
            Classes.class_id.label("class_id"),
            Classes.title.label("title"),
            Classes.chinese_title.label("chinese_title"),
        )
        .select_from(Family)
        .join(Student, Student.family_id == Family.family_id)
        .join(
            StudentClass,
            and_(
                StudentClass.student_id == Student.student_id,
                StudentClass.paid == 0,
                StudentClass.wait == 0,
                StudentClass.year == current_year,
            ),
        )
        .join(Classes, Classes.class_id == StudentClass.class_id)
        .filter(Family.family_id == family.get("family_id"))
        .order_by(Student.dob, StudentClass.class_id)
    )

    results = cart.all()

    final_data = []

    for (
        verified,
        first_name,
        last_name,
        chinese_name,
        sc_obj,
        class_id,
        title,
        chinese_title,
    ) in results:

        item = {
            c.name: getattr(sc_obj, c.name)
            for c in sc_obj.__table__.columns
        }

        item.update({
            "verified": verified,
            "first_name": first_name,
            "last_name": last_name,
            "chinese_name": chinese_name,
            "class_id": class_id,
            "title": title,
            "chinese_title": chinese_title,
        })

        final_data.append(item)

    return final_data


# From payments.php lines 30-39, returns 10 fields, 5 of which are displayed by front-end
@router.get("/payments", status_code = status.HTTP_200_OK)
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
async def view_order_details(db: db_dependency, family: family_dependency, order_id: int):
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
async def view_order_classes(db: db_dependency, family: family_dependency, order_id: int):
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



""" from checkout.php 53-72, don't exactly know what this does
current_year = datetime.now().year
    cart_T1 = (
        db.query(
            Student.first_name.label("first_name"),
            Student.last_name.label("last_name"),
            Student.chinese_name.label("chinese_name"),
            Student.student_id.label("student_id"),
            Classes.class_id.label("class_id"),
        )
        .select_from(Family)
        .join(Student, Student.family_id == Family.family_id)
        .join(StudentClass, and_(StudentClass.student_id == Student.student_id, StudentClass.wait == 0, StudentClass.year == current_year))
        .join( Classes, and_(StudentClass.class_id == Classes.class_id, Classes.class_id == 75))
        .filter(StudentClass.paid == 0)
        .filter(Family.family_id == family.get("family_id"))
        .subquery()
    )
    codes = ['01','02A','02B','07A','07B','08','09A','09B','10B','14','15','16','17','18','19','BOOK']
    cart_T2 = (
        db.query(Student.first_name.label("first_name"),
                Student.last_name.label("last_name"),
                Student.chinese_name.label("chinese_name"),
                Student.student_id.label("student_id"),
                Classes.class_id.label("class_id"))
        .select_from(Family)
        .join(Student, Student.family_id == Family.family_id)
        .join(StudentClass, and_(StudentClass.student_id == Student.student_id, StudentClass.wait == 0, StudentClass.year == current_year))
        .join(Classes, and_(StudentClass.class_id == Classes.class_id, Classes.class_code.in_(codes)))
        .filter(StudentClass.paid == 0)
        .filter(Family.family_id == family.get('family_id'))
        .subquery()
    )

    query = (
    db.query(
        cart_T1.c.first_name,
        cart_T1.c.last_name,
        cart_T1.c.chinese_name,
        cart_T1.c.student_id,
        cart_T1.c.class_id,
    )
    .outerjoin(cart_T2, cart_T1.c.student_id == cart_T2.c.student_id)
    .filter(cart_T2.c.class_id.is_(None))
    )

    results = query.all()

    if results is None:
        raise HTTPException(status_code=204, detail='Cart empty')

    return [
        {
            "first_name": r[0],
            "last_name": r[1],
            "chinese_name": r[2],
            "student_id": r[3],
            "class_id": r[4],
        }
        for r in results
    ]
"""