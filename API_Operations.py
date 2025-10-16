from fastapi import Depends, APIRouter, HTTPException, Path, Query # Import multiple classes from Fast-API package
from starlette import status # Import the status class to retrieve HTTP status codes
from pydantic import BaseModel, Field # Import BaseModel and Field classes for data validation
from sqlalchemy.orm import Session # Import Session class to establish a session between database and server
from typing import Annotated # Import Annotated class to establish dependencies
from Database import LocalSession # Import the LocalSession variable that contains the Session-Maker instance
from Tables import Transaction # Import the Transaction table
from Authentication import get_current_user # Import the function which retrieves information about the user


router_object:APIRouter = APIRouter(
    prefix="/API_Operations", # A new path for any API operations
    tags=["Operations"] # Tags to separate operations
) # API Router instance to establish a path between this module and the main file

def db_connection() -> Session: # Function to establish connection to the database
    connection = LocalSession() # Establish a local session to the database
    try: yield connection # Hold the connection using yield-keyword until the response it sent
    finally: connection.close() # Close the connection once the response has been sent

db_dependency = Annotated[Session, Depends(db_connection)] # Dependency injection that waits for the Session is established by the function
user_dependency = Annotated[dict, Depends(get_current_user)] # Dependency injection that waits for the current user information is retrieved as dictionary


class TransactionRequest(BaseModel): # Request class that inherits from Base-Model for data validation
    amount:float = Field(gt=10.00, description="Current Amount in your Account!") # Field instance to set limits and constraints on input passed by client
    account_type:str = Field(default='Checking', description="Type of Bank Account!") # Field instance with a default value and description outputted to the user


@router_object.get("/transactions", status_code=status.HTTP_200_OK) # GET Request to retrieve all transactions from the database with a 200 OK response if successful
async def get_all_transactions(db:db_dependency): return db.query(Transaction).all() # Query the Transaction table and retrieve all the records

@router_object.get("/transactions/{transaction_id}", status_code=status.HTTP_200_OK) # GET Request to retrieve a record based on the ID passed as dynamic parameter with a 200 OK response if successful
async def get_single_transaction(db:db_dependency, transaction_id:int=Path(gt=0)): # Accept the Session connection to the database and the ID passed as an argument that must be an integer and greater than 0
    transaction_record = db.query(Transaction).filter(Transaction.id == transaction_id).first() # Query the table, filter to retrieve a record with a matching ID passed, and return the first record with the matching ID
    if transaction_record is None: # No records were retrieved from the table
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction History Not Found!") # Raise HTTP-Exception with a status code of 404 (Not-Found) with a message
    else: return f'{transaction_record.owner_id} currently has {transaction_record.amount} dollars!' # Return the record with the matching ID


@router_object.post("/", status_code=status.HTTP_201_CREATED) # POST Request to create a record with a 201 OK response if successful to indicate record was added to database
async def create_transaction(user:user_dependency ,db:db_dependency, transaction: TransactionRequest): # Accept the current user, Session connection to the database, and TransactionRequest instance as an argument
    if user is None: # No current user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User!") # Raise HTTP-Exception to indicate user is un-authorized (401)
    else: # User has been retrieved
        transaction_record = Transaction( # Create transaction record instance
            amount=transaction.amount, # Key-word argument to set amount column with data passed to the request-class instance by the user
            account_type=transaction.account_type, # Key-word argument to set account-type column with data passed to the request-class instance by the user
            owner_id = user.get("Username") # Use the dictionary returned by User-Dependency to retrieve his/her username (primary key on user's table) that is set as the foreign key
        )
        db.add(transaction_record) # Add the record to the table
        db.commit() # Commit changes to the database

@router_object.put("/transactions/", status_code=status.HTTP_204_NO_CONTENT) # PUT Request to update a record with a 204 OK response if successful to indicate record was updated to database
async def update_transaction(db:db_dependency, transaction:TransactionRequest, transaction_id:int=Query(gt=0)): # Accept the database connection, TransactionRequest instance, and ID as a query parameter (/?id=value) that must be greater than 0
    transaction_record = db.query(Transaction).filter(Transaction.id == transaction_id).first() # Query the transaction table, filter the table to retrieve the record that matches the ID passed, and return the first record with matching ID
    if transaction_record is not None: # The matching record was successfully retrieved
        transaction_record.amount = transaction.amount # Access the amount column and set it with the value on the request-instance passed by the client
        transaction_record.account_type = transaction.account_type # Access the account-type column and set it with the value on the request-instance passed by the client
        db.add(transaction_record) # Add the record to the table
        db.commit() # Commit changes to the database
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction Not Found!") # Raise HTTP-Exception to indicate record was not found (404)

@router_object.delete("/transactions/", status_code=status.HTTP_204_NO_CONTENT) # DELETE Request to delete a record with a 204 OK response if successful to indicate record was deleted from the database
async def delete_transaction(db:db_dependency, transaction_id:int=Query(gt=0)): # Accept the database connection and ID as a query parameter (?/id=value) that must be greater than 0
    transaction_record = db.query(Transaction).filter(Transaction.id == transaction_id).first() # Query the transaction table, filter the table to retrieve the record that matches the ID passed, and return the first record with matching ID
    if transaction_record is not None: # The matching record was successfully retrieved
        db.query(Transaction).filter(Transaction.id == transaction_id).delete() # Delete the record from table
        db.commit() # Commit changes to the database
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction Not Found!") # Raise HTTP-Exception to indicate record was not found (404)