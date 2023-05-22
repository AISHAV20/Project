import datetime as dt
import hashlib
import json
from fastapi.encoders import jsonable_encoder
from json import JSONEncoder
from sqlalchemy import desc
from sqlalchemy.orm import Session
import models


class blockchain:
    def mine_block(self, data: str, db: Session) -> dict:
        previous_block = self.get_previous_block(db)
        previous_proof = previous_block.proof
        # cur.execute("""SELECT COUNT(*) FROM BlOCKS""")
        # length=cur.fetchone()
        # index = length[0]+1
        index = (db.query(models.BlockchainModel).count())+1
        proof = self._proof_of_work(previous_proof, index, data)

        previous_hash = self.hash(block=previous_block)
        block = self.create_block(data, proof, previous_hash, index)

        return block

    # creating  a block
    def create_block(
        self, data: str, proof: int, previous_hash: str, index: int
    ) -> dict:
        block = {
            "index": index,
            "data": data,
            "timestamp": str(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "previous_hash": previous_hash,
            "proof": proof
        }
        return block

    def get_previous_block(self, db: Session):
        # return self.chain[-1]
        # cur.execute("""SELECT * FROM BLOCKS ORDER BY id DESC LIMIT 1""")
        # return cur.fetchone()
        # return cur.execute("""SELECT First(*) FROM BLOCKS""")
        return db.query(models.BlockchainModel).order_by(desc(models.BlockchainModel.id)).first()

    def _to_digest(self, new_proof: int, previous_proof: int, index: int, data: str) -> bytes:
        to_digest = str(new_proof*2 - previous_proof*2 + index)+data
        return to_digest.encode()

    def _proof_of_work(self, previous_proof: str, index: int, data: str) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, index, data)
            hash_operation = hashlib.sha3_256(to_digest).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block) -> str:

        # Hash a block and return the crytographic hash of the block
        data_dict = jsonable_encoder(block)
        encoded_block = json.dumps(data_dict, sort_keys=True).encode()
        return hashlib.sha3_256(encoded_block).hexdigest()

    # check blocks
    def is_chain_valid(self, db: Session) -> bool:
        # cur.execute("""SELECT * FROM BLOCKS """)
        # blocks=cur.fetchall()
        # cur.execute("""SELECT * FROM BLOCKS WHERE id = 1 """)
        # previous_block=cur.fetchone()

        previous_block = db.query(models.BlockchainModel).filter(
            models.BlockchainModel.id == 1).first()
        print(previous_block)
        block_index = 2

        # cur.execute("""SELECT COUNT(*) FROM BlOCKS""")
        # length=cur.fetchone()
        length = db.query(models.BlockchainModel).count()
        while block_index < length+1:
            # cur.execute(f"""SELECT * FROM BLOCKS WHERE id = {block_index} """)
            # block=cur.fetchone()
            block = db.query(models.BlockchainModel).filter(
                models.BlockchainModel.id == block_index).first()
            # print(block.previous_hash)
            if block.previous_hash != self.hash(previous_block):
                return False

            # previous_block=db.query(models.BlockchainModel).filter(models.BlockchainModel.id==1).first()
            previous_proof = previous_block.proof
            index = block.id
            data = block.data
            proof = block.proof

            hash_operation = hashlib.sha3_256(self._to_digest(
                new_proof=proof,
                previous_proof=previous_proof,
                index=index,
                data=data)).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block
            block_index += 1
        return True

    def blocks_between_time(self, start_date: str, end_date: str, db: Session):
        start_date = dt.date.fromisoformat(start_date)
        end_date = dt.date.fromisoformat(end_date)

        blocks_in_range = []

        # cur.execute("""SELECT * FROM BLOCKS""")
        # blocks=cur.fetchall()
        blocks = db.query(models.BlockchainModel).all()
        for block in blocks:
            block_date = block.timestamp
            block_date = block_date[:10]
            block_date = dt.date.fromisoformat(block_date)
            if (start_date <= block_date <= end_date):
                blocks_in_range.append(block)

        return blocks_in_range
