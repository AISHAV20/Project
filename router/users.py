from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import models
import uuid
from database import get_db, engine
from schema import (Token,
                    TokenData,
                    User,
                    UserInDB,
                    Register_user,
                    Transaction)

from typing import Optional, Annotated

SECRET_KEY = "Aishav_code_try100+"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router=APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def get_user(username: str, db: Session):
    # cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    # existing_user = cur.fetchone() #->tuple
    existing_user = db.query(models.UserModel).filter(
        models.UserModel.username == username).first()
    if existing_user:
        return existing_user
    return False


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user  # ->returning object #previous-code its tuple


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/signup", tags=["User_Wallet"],
          summary="Creating or Registering user for wallet",
          description="Email must me different")
def signup(register_user: Register_user, db: Session = Depends(get_db)):
    # Check if the username already exists
    # cur.execute("SELECT * FROM users WHERE username = %s", (register_user.username,))
    # existing_user = cur.fetchone()
    existing_user = db.query(models.UserModel).filter(
        models.UserModel.email == register_user.email_id).first()
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

     # Hash the password
    print(register_user.password, "type_of : ", type(register_user.password))
    password_ = register_user.password
    print(type(password_))
    hashed_password = get_password_hash(register_user.password)
    print(hashed_password)
    address = str(uuid.uuid4())  # Generate a unique address for the user

    # Insert the new user into the database
    # cur.execute(
    #     "INSERT INTO users (username,email_id, hashed_password, address) VALUES (%s,%s, %s, %s)",
    #     (register_user.username,register_user.email_id, hashed_password,address),
    # )
    # conn.commit()
    db_data = models.UserModel(username=register_user.username,
                               email=register_user.email_id, hashed_password=hashed_password, address=address)
    db.add(db_data)
    db.commit()
    return {"message": "User created successfully"}


@router.post("/token", response_model=Token, tags=["User_Wallet"])
async def login_for_access_token(
    # -> username and password
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    valid_user = authenticate_user(form_data.username, form_data.password, db)
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": valid_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/transaction", tags=["User_Wallet"],
          summary="All your Transaction is appended when New Block is created ")
async def perform_transaction(transaction: Transaction,
                              current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)):  # -> username and email_id

    print(type(current_user))
    # cur.execute("SELECT * FROM users WHERE username = %s", (current_user[0],))
    # user = cur.fetchone()
    print(current_user.username)

    # cur.execute("SELECT * FROM users WHERE username = %s", (transaction.recipient,))
    # recipient = cur.fetchone()
    recipient_obj = db.query(models.UserModel).filter(
        models.UserModel.username == transaction.recipient).first()
    # print(recipient_obj.username)

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    if not recipient_obj:
        raise HTTPException(status_code=404, detail="Invalid recipient")

    # Check if the sender has sufficient balance
    if current_user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    user_balance = int(current_user.balance)
    user_balance -= transaction.amount
    recipient_amount = int(recipient_obj.balance)
    recipient_amount += transaction.amount

    # # Perform the transaction
    # cur.execute("UPDATE users SET balance = %s WHERE username = %s", (user_balance, user[0]))
    current_user.balance = user_balance
    # cur.execute("UPDATE users SET balance = %s  WHERE username =%s",(recipient_amount, recipient[0]))
    recipient_obj.balance = recipient_amount
    db.commit()

    # transaction = (current_user.username,recipient_obj.username,transaction.amount)
    db_data = models.TransactionModel(
        sender=current_user.username, reciever=recipient_obj.username, amount=transaction.amount)
    db.add(db_data)
    db.commit()

    return ("Transaction successful")


@router.get("/user_transaction", tags=["User_Wallet"])
def user_last_10_transaction(current_user:Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    # (cur.execute("SELECT * FROM transaction where sender= %s",(user,)))
    # return cur.fetchall()
    db_data = db.query(models.TransactionModel).filter(
        models.TransactionModel.sender == current_user.username).all()
    
    dic_data=[]
    for data in db_data:
        dic_data.append({"user":current_user.username,
            "reciever":data.reciever,
            "Amount":data.amount})

    return dic_data