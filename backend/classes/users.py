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
    def __init__(self, id: Optional[str] = None, email: Optional[str] = None, 
                 password: Optional[str] = None, mongo_client: Optional['MongoClient'] = None):
        self._id = ObjectId(id)
        self.email = email
        self.ptf_ids : List[ObjectId] = []
        self.oaths: Dict[str, str] = {}
        self.brokersLastUpdate = {}
        self._password = password
        self._users_db = mongo_client.users
        self._isAuthentificated: bool = False

    def connect_user(self, new_user: bool = False, fast_connect: bool = False):
        if new_user:
            return self._create_user()
        elif fast_connect:
            user = self._users_db.users.find_one({'_id': self._id})
        elif self.email and self._password:
            user = self._users_db.users.find_one({'email': self.email})
        else:
            raise UserError('Email and/or password missing')
        
        if not user:
            raise UserError('No account found with given information')
        
        if fast_connect is False and not self._verify_user(user):
            raise UserError('Password incorrect')
            
        self.from_dict(self, user)
        self._isAuthentificated = True
        
        
    def add_ptf_id(self, ptf_id: str):
        self.ptf_ids.append(ptf_id)
        if self._isAuthentificated or self._verify_user():
            self._users_db.users.find_one_and_update({'_id': self._id}, {'$push': {'ptf_ids': ptf_id}})
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