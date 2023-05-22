from sqlalchemy import Boolean, Column, Integer, String, Float
from database import Base

class BlockchainModel(Base):
        __tablename__="blocks"
        id=Column(Integer,primary_key=True,index=True)
        data=Column(String)
        timestamp=Column(String)
        previous_hash=Column(String)
        proof=Column(Integer)
    
class UserModel(Base):
        __tablename__="users"
        id = Column(Integer, primary_key=True, index=True,autoincrement=True)
        username=Column(String)
        email = Column(String)
        hashed_password = Column(String(length=291))
        address = Column(String)
        balance =Column(Float,default=10)
        
class TransactionModel(Base):
        __tablename__="transaction"
        id = Column(Integer, primary_key=True, index=True,autoincrement=True)
        sender=Column(String)
        reciever=Column(String)
        amount =Column(String)