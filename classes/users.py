import logging
import bcrypt
from typing import List, Dict, TYPE_CHECKING
from bson import ObjectId

from generals import GeneralMethods

if TYPE_CHECKING:
    from pymongo import MongoClient


class User(GeneralMethods):
    def __init__(self, email: str, password:str, mongo_client: 'MongoClient | None' = None, new_user: bool = False):
        self.email = email
        self.ptf_ids : List[ObjectId] = []
        self.oaths: Dict[str, str] = {}
        self.password = password
        self._mongo_client = mongo_client

        if new_user:
            self.create_user()

    def create_user(self):
        user_dict = self.to_dict()
        user_dict['password_hash'] = self._hash_password(self.password)
        self._mongo_client.users.users.insert_one(user_dict)
    
    def add_ptf_id(self, ptf_id: str):
        self.ptf_ids.append(ptf_id)
        if self.verify_user():
            self._mongo_client.users.users.find_one_and_update({'email': self.email}, {'$push': {'ptf_ids': ptf_id}})
        else:
            logging.error('Ptf_id not updated online')

    def connect_user(self):
        if self.email and self.password:
            user = self._mongo_client.users.users.find_one({'email': self.email})
        else:
            raise Exception('Email and/or password missing')
        if self.verify_user(user):
            self.ptf_ids += user['ptf_ids']
            self.oaths.update(user['oaths'])
        else:
            raise Exception('Password incorrect')
            
    def verify_user(self, user: dict | None = None) -> bool:
        if not user:
            user = self._mongo_client.users.users.find_one({'email': self.email})
        if bcrypt.checkpw(self.password.encode('utf-8'), user['password_hash']):
            return True
        return False

    @staticmethod
    def _hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)