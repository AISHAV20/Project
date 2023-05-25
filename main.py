from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import datetime as dt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import models
import uuid
from Blockchain import blockchain
from database import get_db, engine
from schema import (Token,
                    TokenData,
                    User,
                    UserInDB,
                    Register_user,
                    Transaction)

from typing import Optional, Annotated
from router import blocks,users



app = FastAPI()


models.Base.metadata.create_all(bind=engine, checkfirst=True)


app.include_router(blocks.router)#including routers of blocks

# user_creation
app.include_router(users.router)# including routers of users

