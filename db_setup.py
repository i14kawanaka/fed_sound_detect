import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection(u'users').document(u'PredResult')
doc_ref.set({
    u'Cur': 3,
    u'Pre': 2
})
