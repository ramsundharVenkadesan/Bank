from Database import Base # Import the base class that created the database
from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey, Enum # Import the Column class to define columns in table, its data types, and class to establish relationships between tables


class User(Base): # Parent-User table that inherits from the Base class used to construct the database itself
    __tablename__ = "User" # Name of the table
    first_name = Column(String) # Column to store first name of the user (Only strings can be added)
    last_name = Column(String) # Column to store last name of the user (Only strings can be added)
    email = Column(String, unique=True, index=True) # Column to store user's email that must be unique (no duplicates) and indexable to increase performance
    username = Column(String, unique=True, index=True, primary_key=True) # Column to store username that must be unique because its the primary key of the table to uniquely identify each record
    hashed_password = Column(String) # Column to store user's password that is hashed
    flagged = Column(Boolean, default=False) # Column to flag the user
    SSN = Column(String, unique=True, index=True) # Column to store user's SSN that is indexable and unique
    role = Column(Enum('Admin', 'User'), default='User') # A column to store role of the user created and it can only be an admin or user


class Transaction(Base): # Child-Transaction table that inherits from the Base class used to construct the database itself
    __tablename__ = "Transaction" # Name of the table
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Column that represents transaction ID uniquely because it increments automatically as new records are added and is the primary key to identify each row
    amount = Column(Float, default=0.0) # Column to store balance of each user
    account_type = Column(Enum('Checking', 'Credit', 'Savings')) # Column to store account type which only accepts three values defined in the Enum type
    owner_id = Column(String, ForeignKey("User.username")) # Column that references primary key of User's database table (Foreign Key) to link two tables together, allowing to identify which user performed the transaction