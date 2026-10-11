from datetime import datetime
from app import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    pages = db.Column(db.Integer, nullable=True)
    extracted_text = db.Column(db.Text, nullable=True)  # optional storage

    def __repr__(self):
        return f'<Document id={self.id} filename={self.filename}>'
