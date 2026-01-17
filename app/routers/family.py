from fastapi import APIRouter,HTTPException, status
from datetime import datetime
from pydantic import BaseModel, Field
from ..models import Family, VolunteerActivities, VolunteerActivityYear, FamilyYear, UserInfo
from .auth import db_dependency, family_dependency


router = APIRouter(
    prefix = '/family',
    tags = ['family']
)

class InitialFamilyRequest(BaseModel):
    email: str
    password: str           # for now, not hashed until we can implement OAuth
    check_password: str

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

# From signup.php lines 300-335 roughly
@router.post("/profile/create", status_code=status.HTTP_201_CREATED)
async def initial_family_signup(db: db_dependency, req: InitialFamilyRequest):
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
    
    query = db.query(UserInfo).filter(UserInfo.email == req.email).first()
    query.profile_created = True

    now = datetime.utcnow()

    # creating the family profile, generalizing all other fields to be completed later
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

# From profile.php lines 26-44, returns all fields of Family object
@router.get("/profile/view", status_code = status.HTTP_200_OK)
async def get_family(family: family_dependency, db: db_dependency):
    if family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return db.query(Family).filter(Family.family_id == family.get('family_id')).first()


# From profile.php linles 59-65, returns Volunteer History
@router.get("/profile/volunteer", status_code = status.HTTP_200_OK)
async def get_family_volunteer(family: family_dependency, db: db_dependency):
    if family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    volunteer_log = (db.query(VolunteerActivityYear, VolunteerActivityYear.year, VolunteerActivities.volunteer_id.label("code"), VolunteerActivities.name)
                    .join(VolunteerActivities, VolunteerActivities.volunteer_id == VolunteerActivityYear.volunteer_id)
                    .join(FamilyYear, FamilyYear.vay_id == VolunteerActivityYear.vay_id)
                    .filter(FamilyYear.family_id == family.get("family_id"))
                    .filter(FamilyYear.paid != 0)
    )

    results = volunteer_log.all()

    final_log = []
    for row in results:
        item = {
            "year": row.year,
            "code": row.code,
            "name": row.name
        }
        final_log.append(item)

    return final_log


# From edit_profile.php
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

