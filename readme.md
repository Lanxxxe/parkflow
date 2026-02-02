How to run the backend server:

1. Ensure you have Python 3.8+ installed on your machine.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Flask development server:
   ```bash
   python app.py
   ```
   


**Backlogs**

- Transaction ID 
- Time In
- Parking Duration
- Slot Taken
- Rate
- Plate Number
- Vehicle Model

**Live Map**
- Car Model
- Lot Status (Occupied/Vacant)
- Slot Number
- Slot ID

**Dashboard**
- Monthly Earnings
- Daily Earnings
- Monthly Transactions
- Parking Slots (# of Occupied and # of Vacant)

**Payments**
- Plate Number
- Vehicle Model
- Choosed Slot
- Duration (Amount)

**Receipts**
- Transaction ID
- Plate Number
- Vehicle Model
- Slot Number
- Parking Duration


**Login Admin**
- Username
- Password


