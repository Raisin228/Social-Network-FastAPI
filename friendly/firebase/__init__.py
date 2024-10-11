import firebase_admin
from config import settings
from firebase_admin import credentials

cred = credentials.Certificate(settings.FIREBASE_CONFIG_FILE)
firebase_admin.initialize_app(cred)
