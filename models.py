from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
        # short, debug-friendly
        return f"<TrainingSubmissions id={self.id} email={self.email!r} status={self.status!r}>"

    def __str__(self):
        # human-friendly
        return f"TrainingSubmission #{self.id} for {self.email} on {self.train_date:%Y-%m-%d}"

    

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    can_edit_employees = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

