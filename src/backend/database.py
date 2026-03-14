"""
MongoDB database configuration and setup for Mergington High School API
"""

from pymongo import MongoClient
from argon2 import PasswordHasher

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mergington_high']
activities_collection = db['activities']
teachers_collection = db['teachers']
bank_users_collection = db['bank_users']
bank_accounts_collection = db['bank_accounts']
bank_transactions_collection = db['bank_transactions']

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

    # Initialize banking data if empty
    if bank_users_collection.count_documents({}) == 0:
        for user in initial_bank_users:
            bank_users_collection.insert_one({"_id": user["username"], **user})

    if bank_accounts_collection.count_documents({}) == 0:
        for account in initial_bank_accounts:
            bank_accounts_collection.insert_one({"_id": account["account_number"], **account})

    if bank_transactions_collection.count_documents({}) == 0:
        for transaction in initial_bank_transactions:
            bank_transactions_collection.insert_one(transaction)

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]

initial_bank_users = [
    {
        "username": "jsmith",
        "display_name": "Jane Smith",
        "password": hash_password("bank123"),
        "email": "jane.smith@example.com",
        "phone": "555-0101",
        "address": "123 Main St, Springfield, IL 62701"
    },
    {
        "username": "bjones",
        "display_name": "Bob Jones",
        "password": hash_password("secure456"),
        "email": "bob.jones@example.com",
        "phone": "555-0202",
        "address": "456 Oak Ave, Springfield, IL 62702"
    }
]

initial_bank_accounts = [
    {
        "account_number": "CHK-001-001",
        "owner_username": "jsmith",
        "account_type": "checking",
        "account_name": "Primary Checking",
        "balance": 4250.75,
        "currency": "USD",
        "status": "active"
    },
    {
        "account_number": "SAV-001-001",
        "owner_username": "jsmith",
        "account_type": "savings",
        "account_name": "High-Yield Savings",
        "balance": 12800.00,
        "currency": "USD",
        "status": "active"
    },
    {
        "account_number": "CC-001-001",
        "owner_username": "jsmith",
        "account_type": "credit",
        "account_name": "Rewards Credit Card",
        "balance": -950.30,
        "credit_limit": 5000.00,
        "currency": "USD",
        "status": "active"
    },
    {
        "account_number": "CHK-002-001",
        "owner_username": "bjones",
        "account_type": "checking",
        "account_name": "Primary Checking",
        "balance": 2100.50,
        "currency": "USD",
        "status": "active"
    },
    {
        "account_number": "SAV-002-001",
        "owner_username": "bjones",
        "account_type": "savings",
        "account_name": "Emergency Fund",
        "balance": 8500.00,
        "currency": "USD",
        "status": "active"
    }
]

initial_bank_transactions = [
    {
        "transaction_id": "TXN-001",
        "account_number": "CHK-001-001",
        "type": "debit",
        "amount": 62.50,
        "description": "Grocery Store - Fresh Market",
        "category": "Food & Dining",
        "date": "2026-03-12",
        "balance_after": 4250.75
    },
    {
        "transaction_id": "TXN-002",
        "account_number": "CHK-001-001",
        "type": "credit",
        "amount": 3200.00,
        "description": "Direct Deposit - Payroll",
        "category": "Income",
        "date": "2026-03-10",
        "balance_after": 4313.25
    },
    {
        "transaction_id": "TXN-003",
        "account_number": "CHK-001-001",
        "type": "debit",
        "amount": 120.00,
        "description": "Electric Bill - City Power",
        "category": "Bills & Utilities",
        "date": "2026-03-08",
        "balance_after": 1113.25
    },
    {
        "transaction_id": "TXN-004",
        "account_number": "CHK-001-001",
        "type": "debit",
        "amount": 45.99,
        "description": "Netflix Subscription",
        "category": "Entertainment",
        "date": "2026-03-07",
        "balance_after": 1233.25
    },
    {
        "transaction_id": "TXN-005",
        "account_number": "CHK-001-001",
        "type": "debit",
        "amount": 200.00,
        "description": "Transfer to Savings",
        "category": "Transfer",
        "date": "2026-03-05",
        "balance_after": 1279.24
    },
    {
        "transaction_id": "TXN-006",
        "account_number": "SAV-001-001",
        "type": "credit",
        "amount": 200.00,
        "description": "Transfer from Checking",
        "category": "Transfer",
        "date": "2026-03-05",
        "balance_after": 12800.00
    },
    {
        "transaction_id": "TXN-007",
        "account_number": "SAV-001-001",
        "type": "credit",
        "amount": 32.50,
        "description": "Interest Payment",
        "category": "Interest",
        "date": "2026-03-01",
        "balance_after": 12600.00
    },
    {
        "transaction_id": "TXN-008",
        "account_number": "CC-001-001",
        "type": "debit",
        "amount": 89.99,
        "description": "Amazon Purchase",
        "category": "Shopping",
        "date": "2026-03-11",
        "balance_after": -950.30
    },
    {
        "transaction_id": "TXN-009",
        "account_number": "CC-001-001",
        "type": "debit",
        "amount": 35.00,
        "description": "Gas Station - QuickFuel",
        "category": "Auto & Transport",
        "date": "2026-03-09",
        "balance_after": -860.31
    },
    {
        "transaction_id": "TXN-010",
        "account_number": "CC-001-001",
        "type": "credit",
        "amount": 300.00,
        "description": "Payment - Thank You",
        "category": "Payment",
        "date": "2026-03-03",
        "balance_after": -825.31
    }
]

