from fastapi import APIRouter,HTTPException, status
from sqlalchemy import func, desc
from models import Family, Order, OrderStudentClass, StudentClass, Student, Classes, VolunteerActivities, VolunteerActivityYear, FamilyYear
from .auth import db_dependency, family_dependency


router = APIRouter(
    prefix = '/family',
    tags = ['payments']
)


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

