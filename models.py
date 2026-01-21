from extensions import db
from datetime import datetime

class UserSubmission(db.Model):
    __tablename__ = "user_submissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserSubmission {self.name}>"
