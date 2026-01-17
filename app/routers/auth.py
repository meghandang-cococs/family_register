"""
Filename: auth.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Authentication, session, third-party OAuth (Google, Facebook, Yahoo)
"""

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Annotated
from pydantic import BaseModel
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth, OAuthError
import os 
from dotenv import load_dotenv
from ..models import Family, UserInfo
from ..database import SessionLocal 


router = APIRouter(
    tags = ['auth']
)


SECRET_KEY = 'bc74bb305941d6500df275cd41bb699f6cd81152c56291d03b909e6dca48d908'   # change this
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

# google log in

load_dotenv()
CLIENT_ID = os.environ.get('google-id', None)
CLIENT_SECRET = os.environ.get('google-secret', None)

oauth = OAuth()
oauth.register(
    name = 'google',
    server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration',
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    client_kwargs = {
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8080/auth/google'
    }
)    


@router.get("/login/google")
async def login_google(request: Request): 
    url = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, url)


@router.get('/auth/google', response_model = Token)
async def auth_google(request: Request, db: db_dependency): 
    try: 
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    user = token.get('userinfo')
    exists_in_user_info = db.query(UserInfo).filter(UserInfo.email == user.get('email')).first()

    if not exists_in_user_info:      # if completely new user
        if user:
            db = SessionLocal()
            userinfo = UserInfo(
                email=user.get('email'), 
                first_name=user.get('given_name'),
                last_name=user.get('family_name'),
                profile_created=False,           # will prompt user to fill out family profile
                token_=token
            )
            db.add(userinfo)
            db.commit()
            db.close()
            return {"access_token": token["access_token"], "token_type": "bearer"}
    else:
        exists_in_family = db.query(Family).filter(Family.email == user.get('email'))
        if exists_in_family:              # if in family database
            return {"access_token": token["access_token"], "token_type": "bearer"}
        else: 
            exists_in_user_info.profile_created = False
    
    raise HTTPException(status_code=400, detail="User info not found")   


# log in with facebook

CLIENT_ID = os.environ.get('facebook-id', None)
CLIENT_SECRET = os.environ.get('facebook-secret', None)


oauth.register(
    name = 'facebook', 
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    authorize_url="https://www.facebook.com/v20.0/dialog/oauth",
    access_token_url="https://graph.facebook.com/v20.0/oauth/access_token",
    api_base_url="https://graph.facebook.com/",
    client_kwargs={"scope": "email"},
) 


@router.get("/login/facebook")
async def login_fb(request: Request):
    redirect_uri = request.url_for("auth_fb")  
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get('/auth/facebook', response_model = Token)
async def auth_fb(request: Request, db: db_dependency):
    try:
        token = await oauth.facebook.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch user profile from Facebook Graph API
    # fields: add/remove as needed
    resp = await oauth.facebook.get(
        "me",
        token=token,
        params={"fields": "id, first_name, last_name ,email"},
    )
    user = resp.json()

    email = user.get("email")
    if not email:
        # either permission wasn't granted or FB account has no email
        raise HTTPException(
            status_code=400,
            detail="Facebook did not return an email. Ensure 'email' permission is granted and the FB account has an email."
        )

    exists_in_user_info = (
        db.query(UserInfo).filter(UserInfo.email == email).first()
    )

    if not exists_in_user_info:
        userinfo = UserInfo(
            email=email,
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            profile_created=False,
            token_=token
        )
        db.add(userinfo)
        db.commit()
        db.refresh(userinfo)
        return {"access_token": token["access_token"], "token_type": "bearer"}

    exists_in_family = db.query(Family).filter(Family.email == email).first()
    if exists_in_family:
        return {"access_token": token["access_token"], "token_type": "bearer"}

    exists_in_user_info.profile_created = False
    db.commit()
    return {"access_token": token["access_token"], "token_type": "bearer"}


# log in with yahoo

CLIENT_ID = os.environ.get('yahoo-id', None)
CLIENT_SECRET = os.environ.get('yahoo-secret', None)

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing YAHOO_ID or YAHOO_SECRET")


oauth.register(
    name="yahoo",
    server_metadata_url="https://api.login.yahoo.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"}
)


@router.get("/login/yahoo")
async def login_yh(request: Request):
    redirect_uri = "https://somesite.com"   # temporary. yahoo only takes https for redirect url, so i could not route it to /auth/yahoo
    print("YAHOO redirect_uri:", redirect_uri)
    print("YAHOO client_id:", CLIENT_ID)
    return await oauth.yahoo.authorize_redirect(request, redirect_uri)


@router.get('/auth/yahoo', response_model = Token)
async def auth_yh(request: Request, db: db_dependency):
    try:
        token = await oauth.yahoo.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

  
    resp = await oauth.yahoo.get("userinfo", token=token)
    user = resp.json()

    email = user.get("email")
    if not email:
        raise HTTPException(
            status_code=400,
            detail="yahoo did not return an email. Ensure 'email' permission is granted and the yahoo account has an email."
        )

    exists_in_user_info = (
        db.query(UserInfo).filter(UserInfo.email == email).first()
    )

    if not exists_in_user_info:
        userinfo = UserInfo(
            email=email,
            first_name=user.get("given_name"),
            last_name=user.get("family_name"),
            profile_created=False,
            token_=token
        )
        db.add(userinfo)
        db.commit()
        db.refresh(userinfo)
        return {"access_token": token["access_token"], "token_type": "bearer"}

    exists_in_family = db.query(Family).filter(Family.email == email).first()
    if exists_in_family:
        return {"access_token": token["access_token"], "token_type": "bearer"}

    exists_in_user_info.profile_created = False
    db.commit()
    return {"access_token": token["access_token"], "token_type": "bearer"}


# log in for token, non oauth
@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    profile = authenticate_user(form_data.username, form_data.password, db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')
    token = create_access_token(profile.email, profile.family_id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
