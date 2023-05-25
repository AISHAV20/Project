from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status,APIRouter
import uuid
import datetime as dt
import models
from Blockchain import blockchain
from database import get_db, engine
from typing import Optional

router=APIRouter()
blockchain = blockchain()


@router.post("/mine_block/", tags=["Blockchain"])
def mine_block(dataa: str, db: Session = Depends(get_db)):
    if not (db.query(models.BlockchainModel).filter(models.BlockchainModel.id == 1).first()):
        db_user = models.BlockchainModel(id=1, data="hi", timestamp=str(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                                         previous_hash="0", proof=1)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # print(block.proof)

    block = blockchain.mine_block(dataa, db)
    # print(block,type(block))
    # print(block['index'])
    db.add(models.BlockchainModel(id=block["index"], data=block["data"], timestamp=block["timestamp"],
                                  previous_hash=block["previous_hash"], proof=block["proof"]))
    db.commit()
    return block


@router.get("/blockchain", tags=["Blockchain"])
def get_blockchain(db: Session = Depends(get_db)):
    if not blockchain.is_chain_valid(db):
        return HTTPException(status_code=404, detail="Invalid blockchain")
    # chain=blockchain.chain
    # cur.execute("""SELECT * FROM Blocks""")
    # return cur.fetchall()
    return db.query(models.BlockchainModel).all()


@router.get("/valid/", tags=["Blockchain"])
def check_valid(db: Session = Depends(get_db)):
    return blockchain.is_chain_valid(db)


@router.get("/previous_block/", tags=["Blockchain"])
def previous_block(db: Session = Depends(get_db)):
    return blockchain.get_previous_block(db)


@router.get("/hash_by_block_number/{index}", tags=["Blockchain"])
def get_hash_by_block_number(index: int, db: Session = Depends(get_db)):
    # return blockchain.chain[index+1]["previous_hash"]
    # cur.execute(f"""SELECT previous_hash FROM BLOCKS WHERE id = {index} """)
    # return  cur.fetchone()
    block = db.query(models.BlockchainModel).filter(
        models.BlockchainModel.id == index).first()
    return block.previous_hash


@router.get("/block_number/{index}", tags=["Blockchain"])
def get_block_by_index(index: int, db: Session = Depends(get_db)):
    # cur.execute(f"""SELECT * FROM BLOCKS WHERE id = {index} """)
    # return  cur.fetchone()
    return db.query(models.BlockchainModel).filter(models.BlockchainModel.id == index).first()


@router.get("/block_between_time/{start_date}/{end_date}", tags=["Blockchain"])
def block_between_time(start_date: str, end_date: str, db: Session = Depends(get_db)):
    # return f"start_date{start_date} and end_date {end_date}"
    if not blockchain.is_chain_valid(db):
        return HTTPException(status_code=404, details="Invalid blockchain")
    return blockchain.blocks_between_time(start_date, end_date, db)