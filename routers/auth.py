from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import Family


router = APIRouter(
    tags = ['auth']
)


SECRET_KEY = 'bc74bb305941d6500df275cd41bb699f6cd81152c56291d03b909e6dca48d908'
ALGORITHM = 'HS256'
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = 'token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_family(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        email : str = payload.get('sub')
        family_id: int = payload.get('id')

        if email is None or family_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                                detail = 'Could not validate credentials')
        return {'email': email, 'family_id': family_id}
    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)        


db_dependency = Annotated[Session, Depends(get_db)]
family_dependency = Annotated[dict, Depends(get_current_family)]


class CreateFamilyRequest(BaseModel):
    email: str
    password: str
    check_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(email: str, password: str, db):
    profile = db.query(Family).filter(Family.email == email).first()
    if not profile:
        return False
    if not password == profile.password:
        return False
    return profile


def create_access_token(email: str, family_id: int, expires_delta: timedelta):
    encode = {'sub': email, 'id': family_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    
@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    profile = authenticate_user(form_data.username, form_data.password, db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')
    token = create_access_token(profile.email, profile.family_id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}