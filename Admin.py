from typing import Annotated # Import Annotated class to establish dependencies
from sqlalchemy.orm import Session # Import Session class to establish a session between database and server
from fastapi import APIRouter, Depends, HTTPException, Path # Import multiple classes from Fast-API package
from starlette import status # Import the status class to retrieve HTTP status codes
from Database import LocalSession # Import the LocalSession variable that contains the Session-Maker instance
from Authentication import get_current_user # Import the function which retrieves information about the logged-in user
from Tables import * # Import the User and Transaction tables from the database

admin_router:APIRouter = APIRouter(
    prefix="/Admin", # A new path for any API operations for administrators
    tags=["Administrator"] # # Tags to separate operations
) # API Router instance to establish a path between this module and the main file

def get_database() -> Session: # Function to establish connection to the database
    session = LocalSession() # Establish a local session to the database
    try: yield session # Hold the connection using yield-keyword until the response it sent
    finally: session.close() # Close the connection once the response has been sent


db_dependency = Annotated[Session, Depends(get_database)] # Dependency injection that waits for the Session is established by the function
user_dependency = Annotated[dict, Depends(get_current_user)] # Dependency injection that waits for the current user information is retrieved as dictionary

@admin_router.get("/transaction", status_code=status.HTTP_200_OK) # GET Request to retrieve all transactions from the database with a 200 OK response if successful
async def read_all(user: user_dependency, db:db_dependency): # Accepts the data retrieved from current user and session to the database
    if (user is None) or (user.get('Role') != 'Admin'): # No information retrieved from user or the user logged in is not an administrator
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not an Administrator!') # Raise HTTP-Exception to indicate user is un-authorized (401)
    else: db.query(Transaction).all() # Query the Transaction table and retrieve all the records from all users


@admin_router.delete('/transaction/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT) # DELETE Request to delete a record with a 204 OK response if successful to indicate record was deleted from the database
async def delete(user:user_dependency, db:db_dependency, transaction_id: int=Path(gt=0)): # Accept the database connection ID as a path parameter that must be greater than 0, and information regarding current user
    if (user is None) or (user.get('Role') != 'Admin'): # No information retrieved from user or the user logged in is not an administrator
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not an Administrator!') # Raise HTTP-Exception to indicate user is un-authorized (401)
    else: # User is an administrator
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first() # Retrieve the first record that matches the ID passed by the administrator as a path-argument
        if transaction is None: # No transaction of the ID passed exist
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Transaction not found!') # Raise HTTP-Exception to indicate record was not found (404)
        else: # Matching transaction found in database
            db.query(Transaction).filter(Transaction.id == transaction_id).delete() # Delete the record from the table
            db.commit() # Commit changes to the database
