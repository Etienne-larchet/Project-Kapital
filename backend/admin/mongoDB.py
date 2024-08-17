from django.conf import settings
from pymongo import MongoClient

mongo_status = getattr(settings, "MONGO_ONLINE", None)
if mongo_status:
    url = getattr(settings, "MONGO_API", None)
else:
    url = None

mongo_client = MongoClient(url)
