from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy import func, extract
    
from sqlalchemy.exc import IntegrityError
from models import ParkingSlot, Transaction, Users, db
from flask_cors import CORS
from datetime import datetime, timezone

import os


app = Flask(__name__)
CORS(app, 
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False
)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "parkflow.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return "Welcome to the Parking Management System"

@app.route('/login', methods=['POST'])
def login():        

    data = request.get_json()
    print(data)
    email = data.get('email')
    password = data.get('password')

    try:
        user = Users.validate_user(email, password)
        print(user)
        if user is not None:
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": user.to_dict()
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred during login"
        }), 500
    

@app.route('/insert-db')
def register_db():
    users = [
        {'email': 'admin@gmail.com', 'password': 'admin123', 'role': 'admin'},
        {'email': 'customer@gmail.com', 'password': 'customer123', 'role': 'customer'},
    ]

    try:
        # Insert users
        for user_data in users:
            if Users.query.filter_by(email=user_data['email']).first():
                continue  # skip existing users

            user = Users(
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                role=user_data['role']
            )
            db.session.add(user)

        # Insert parking slots A1 to A10
        for i in range(1, 11):
            slot_number = f'A{i}'
            if ParkingSlot.query.filter_by(slot_number=slot_number).first():
                continue  # skip existing slots

            parking_slot = ParkingSlot(
                slot_number=slot_number,
                status='available'
            )
            db.session.add(parking_slot)

        db.session.commit()

        added_users = Users.get_all_users()
        parking_slots = ParkingSlot.get_all_slots()
        return jsonify({
            "success": True,
            "message": "Users and parking slots registered successfully",
            "users" : [user.email for user in added_users],
            "parking_slots": [slot.slot_number for slot in parking_slots]
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Data already exists"
        }), 409

@app.route('/metrics', methods=['GET'])
def get_metrics():

    # Current date info
    now = datetime.now(timezone.utc)
    current_year = now.year
    current_month = now.month
    today = now.date()
    
    # 1. Monthly Earnings - sum of amount_paid for completed transactions this month
    monthly_earnings = db.session.query(func.sum(Transaction.amount_paid)).filter(
        extract('year', Transaction.created_at) == current_year,
        extract('month', Transaction.created_at) == current_month,
        Transaction.status == 'Paid'
    ).scalar() or 0
    
    # 2. Daily Earnings - sum of amount_paid for completed transactions today
    daily_earnings = db.session.query(func.sum(Transaction.amount_paid)).filter(
        func.date(Transaction.created_at) == today,
        Transaction.status == 'Paid'
    ).scalar() or 0
    
    # 3. Monthly Transactions
    monthly_transactions = db.session.query(func.count(Transaction.id)).filter(
        extract('year', Transaction.created_at) == current_year,
        extract('month', Transaction.created_at) == current_month
    ).scalar() or 0
    
    # 4. Number of Available parking slots
    available_slots = ParkingSlot.query.filter_by(status='available').count()
    
    # 5. Number of Taken parking slots
    taken_slots = ParkingSlot.query.filter_by(status='taken').count()
    
    return jsonify({
        "success": True,
        "metrics": {
            "monthly_earnings": float(monthly_earnings),
            "daily_earnings": float(daily_earnings),
            "monthly_transactions": monthly_transactions,
            "available_slots": available_slots,
            "taken_slots": taken_slots,
            "total_slots": available_slots + taken_slots
        }
    }), 200

@app.route('/parkingSlots', methods=['GET'])
def get_parking_slots():
    slots = ParkingSlot.get_all_slots()
    slots_data = [
        {
            'id': slot.id,
            'slot_number': slot.slot_number,
            'status': slot.status,
        } for slot in slots
    ]
    
    return jsonify({
        "success": True,
        "parking_slots": sorted(slots_data, key=lambda x: x['slot_number'])
    }), 200


@app.route('/updateSlotStatus', methods=['PUT'])
def update_slot_status():
    print(request.json)
    data = request.get_json()
    slot_number = data.get('slot_number')
    status = data.get('status')
    print(slot_number, status)
    if slot_number is None or status is None:
        return jsonify({
            "success": False,
            "message": "slot_number and status are required"
        }), 400

    slot = ParkingSlot.update_slot_status(slot_number, status)
    if slot:
        return jsonify({
            "success": True,
            "message": f"Slot {slot.slot_number} status updated",
            "slot": {
                "id": slot.id,
                "slot_number": slot.slot_number,
                "status": slot.status
            }
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Slot not found"
        }), 404


@app.route('/getAllTransactions', methods=['GET'])
def get_all_transactions():
    transactions = Transaction.get_all_transactions()

    transactions_data = [
        {
            'id': transaction.id,
            'transaction_id': transaction.transaction_id,
            'plate_number': transaction.plate_number,
            'vehicle_model': transaction.vehicle_model,
            'slot_id': transaction.slot_id,
            'time_in': transaction.time_in,
            'time_out': transaction.time_out,
            'rate': str(transaction.rate),
            'amount_paid': str(transaction.amount_paid) if transaction.amount_paid else None,
            'status': transaction.status
        } for transaction in transactions
    ]
    return jsonify({
        "success": True,
        "transactions": transactions_data
    }), 200


@app.route('/addTransaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    transaction_id = data.get('id')
    plate_number = data.get('plateNumber')
    vehicle_model = data.get('vehicleModel')
    slot_number = data.get('slotCode')
    duration = data.get('duration')
    rate = data.get('price')
    status = data.get('status')

    print(data)
    if not all([transaction_id, plate_number, vehicle_model, slot_number, duration, rate, status]):
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    slot_id = ParkingSlot.get_slot_by_number(slot_number)

    transaction = Transaction.add_transaction(
        transaction_id,
        plate_number,
        vehicle_model,
        slot_id.id,
        duration,
        rate,
        status
    )

    return jsonify({
        "success": True,
        "message": "Transaction added successfully",
        "transaction": {
            "id": transaction.id,
            "transaction_id": transaction.transaction_id,
            "plate_number": transaction.plate_number,
            "vehicle_model": transaction.vehicle_model,
            "slot_id": transaction.slot_id,
            "duration": str(transaction.duration),
            "amount_paid": str(transaction.amount_paid),
            "status": transaction.status
        }
    }), 201


if __name__ == '__main__':
    app.run(debug=True)