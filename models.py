import datetime
from flask import url_for
from nomic import db

class Proposal(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    created_by = db.StringField(max_length=255, required=False)
    number = db.StringField(max_length=255, required=True)
    votes_revealed = db.BooleanField(default=False)
    archived = db.BooleanField(default=False)
    votes = db.ListField(db.EmbeddedDocumentField('Vote'))

    def __unicode__(self):
        return self.number

    def get_absolute_url(self):
        return url_for('proposal', kwargs={"number": self.number})

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'number'],
        'ordering': ['-created_at']
    }

class Vote(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    vote = db.StringField(max_length=255, required=True)
    hate_upon = db.StringField(max_length=255, required=False)
