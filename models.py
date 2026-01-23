from extensions import db
from datetime import datetime

class UserSubmission(db.Model):
    __tablename__ = "user_submissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    def to_dict(self):
        # Only include table columns (skips relationships & SA internals)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


    def __repr__(self):
        return f"<UserSubmission {self.name}>"
    

class TrainingSubmissions(db.Model):
    __tablename__ = "training_submissions"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100))
    training = db.Column(db.String(250))
    train_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    def to_dict(self):
        # Only include table columns (skips relationships & SA internals)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


    def __repr__(self):
        return f"<UserSubmission {self.name}>"
