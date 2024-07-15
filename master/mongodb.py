from pymongo import MongoClient
from django.conf import settings


status = getattr(settings, 'MONGO_ONLINE', None)
if status:
    url = getattr(settings, 'MONGO_API', None)
else:
    url = None

mongo_client = MongoClient(url)