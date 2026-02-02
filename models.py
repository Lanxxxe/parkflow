from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import check_password_hash
from flask import jsonify

db = SQLAlchemy()


class ParkingSlot(db.Model):
    """Represents a parking slot in the parking lot"""
    __tablename__ = 'parking_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    slot_number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(10), default='available', nullable=False)  # taken or available
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    transactions = db.relationship('Transaction', backref='parking_slot', lazy=True)
    
    def __repr__(self):
        return f'<ParkingSlot {self.slot_number}>'
    
    @classmethod
    def get_all_slots(cls):
        return cls.query.order_by(cls.slot_number).all()
    

    @classmethod
    def get_slot_by_number(cls, slot_number):
        return cls.query.filter_by(slot_number=slot_number).first()

    @classmethod
    def add_slot(cls, slot_number):
        new_slot = cls(slot_number=slot_number)
        db.session.add(new_slot) # INSERT INTO 
        db.session.commit()
        return new_slot
    
    @classmethod
    def update_slot_status(cls, slot_number, status):
        slot = cls.query.filter_by(slot_number=slot_number).first()
        if slot:
            slot.status = status
            db.session.commit()

        return slot
    
    @classmethod
    def get_available_slots(cls):
        return cls.query.filter_by(status='available').order_by(cls.slot_number).all()

class Transaction(db.Model):
    """Represents a parking transaction"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    plate_number = db.Column(db.String(20), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slots.id'), nullable=False)
    time_in = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    time_out = db.Column(db.DateTime, nullable=True)
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    duration=db.Column(db.String, nullable=False)  # duration in hours
    amount_paid = db.Column(db.Numeric(10, 2), nullable=True)
    status = db.Column(db.String(10), default='active', nullable=False)  # active or completed
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f'<Transaction {self.id} - {self.plate_number}>'
    
    @property
    def parking_duration(self):
        """Calculate parking duration in hours"""
        if self.time_out:
            delta = self.time_out - self.time_in
            return delta.total_seconds() / 3600
        return None
    
    @classmethod
    def get_all_transactions(cls):
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def add_transaction(cls, transaction_id, plate_number, vehicle_model, slot_id,duration, rate, status):
        new_transaction = cls(
            transaction_id = transaction_id,
            plate_number=plate_number,
            vehicle_model=vehicle_model,
            slot_id=slot_id,
            duration=duration,
            amount_paid=rate,
            rate=rate,
            status=status
        )
        db.session.add(new_transaction)
        db.session.commit()
        return new_transaction


class Users(db.Model):
    """Represents Users for login"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed password
    role = db.Column(db.String(20), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role
        }
    
    @classmethod
    def get_all_users(cls):
        return cls.query.order_by(cls.email).all()


    @classmethod
    def validate_user(cls, email, password):
        try:
            if not email or not password:
                raise ValueError("Email and password are required")
            
            email = str(email)
            password = str(password)

            user = cls.query.filter_by(email=email).first()
            
            if not user:
                raise ValueError("User does not exist")

            if not check_password_hash(user.password, password):
                raise ValueError("Incorrect password")
            
            return user
        except Exception:
            return None
        