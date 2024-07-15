import logging
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional, TYPE_CHECKING
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from .generals import GeneralMethods

if TYPE_CHECKING:
    from pymongo import MongoClient


class UserError(Exception):
    pass


class User(GeneralMethods):
    def __init__(self, email: str, password: str, mongo_client: Optional['MongoClient'] = None):
        self.email = email
        self.ptf_ids : List[ObjectId] = []
        self.oaths: Dict[str, str] = {}
        self._password = password
        self._users_db = mongo_client.users
        self._id = ObjectId()

    def connect_user(self, new_user: bool = False):
        if new_user:
            return self._create_user()
        if self.email and self._password:
            user = self._users_db.users.find_one({'email': self.email})
            if not user:
                raise UserError('No account with this email')
        else:
            raise UserError('Email and/or password missing')
        if self._verify_user(user):
            self.ptf_ids += user['ptf_ids']
            self.oaths.update(user['oaths'])
            self._id = user['_id']
        else:
            raise UserError('Password incorrect')
        
    def add_ptf_id(self, ptf_id: str):
        self.ptf_ids.append(ptf_id)
        if self.verify_user():
            self._users_db.users.find_one_and_update({'email': self.email}, {'$push': {'ptf_ids': ptf_id}})
        else:
            logging.error('Ptf_id not updated online')

    def generate_token(self = None, duration: int = 20) -> dict:
        token = secrets.token_urlsafe(50)
        expiration = datetime.now() + timedelta(minutes=duration)
        result = {
            'value': token,
            'expiration': expiration
        }
        if self:
            self._users_db.tokens.find_one_and_update({'_id': self._id}, {'$set': {'token': result}}, upsert=True)
        return result
 
    def _create_user(self):
        user_dict = self.to_dict()
        user_dict['password_hash'] = self.hash(self._password)
        user_dict['_id'] = self._id
        try:
            self._users_db.users.insert_one(user_dict)
        except DuplicateKeyError:
            raise UserError('Email already used')
            
    def _verify_user(self, user: Optional[dict] = None) -> bool:
        if not user:
            user = self._users_db.users.find_one({'email': self.email})
        if bcrypt.checkpw(self._password.encode('utf-8'), user['password_hash']):
            return True
        return False
    
    @staticmethod
    def hash(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)