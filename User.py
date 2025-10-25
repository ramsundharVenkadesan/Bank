from typing import Annotated # Import Annotated class to establish dependencies
from Tables import User # Import the User table from the database
from fastapi import APIRouter, Depends, HTTPException # Import multiple classes from Fast-API package
from starlette import status # Import the status class to retrieve HTTP status codes
from Authentication import get_current_user, verification # Import the function which retrieves information about the logged-in user and verifies the credentials
from sqlalchemy.orm import Session # Import Session class to establish a session between database and server
from Database import LocalSession # Import the LocalSession variable that contains the Session-Maker instance
from hashlib import sha512 # Import SHA-512 hashing algorithm
from pydantic import BaseModel, Field # Import BaseModel and Field classes for data validation


user_router:APIRouter = APIRouter(
    prefix="/About-User", # A new path for any API operations for any user
    tags=["Profile"] # Tags to separate operations
) # API Router instance to establish a path between this module and the main file

class UserVerification(BaseModel): # User-Verification Request class that inherits BaseModel for data validation
    password: str # The current password on user
    new_password: str = Field(min_length=5) # New password entered by the use

def get_database() -> Session: # Function to establish connection to the database
    session = LocalSession() # Establish a local session to the database
    try: yield session # Hold the connection using yield-keyword until the response it sent
    finally: session.close() # Close the connection once the response has been sent

user_dependency = Annotated[dict, Depends(get_current_user)] # Dependency injection that waits for the Session is established by the function
db_dependency = Annotated[Session, Depends(get_database)] # Dependency injection that waits for the current user information is retrieved as dictionary

@user_router.get("/user", status_code=status.HTTP_200_OK) # GET Request to retrieve the current user's profile from the database with a 200 OK response if successful
async def get_user(user:user_dependency, db:db_dependency): # Accepts the data retrieved from current user and session to the database
    if user is None: # No information retrieved from user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") # Raise HTTP-Exception to indicate profile was not found (404)
    else: return db.query(User).filter(user.get('Username') == User.username).first() # Retrieve the first record that matches the username of the current logged in user

@user_router.put("/user/password", status_code=status.HTTP_204_NO_CONTENT) # PUT Request to retrieve the change user's password from the database with a 204 OK response if successful
async def update_password(user:user_dependency, db:db_dependency, verify:UserVerification): # Accepts the data retrieved from current user, session to the database, and new password entered by the user
    if user is None: # No information retrieved from user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") # Raise HTTP-Exception to indicate profile was not found (404)
    else: # User with valid credentials
        user_model = db.query(User).filter(user.get('Username') == User.username).first() # Retrieve the first record that matches the username of the current logged in user
        if not verification(user_model.hashed_password, verify.password): # Verify the current password of the user with the hashed password of the user stored in the database
            raise HTTPException(status_code=status.HTTP_401_NOT_AUTHORIZED, detail="Incorrect password") # Raise HTTP-Exception to indicate user is un-authorized (401)
        else: # Credentials are verified
            user_model.hashed_password = sha512(verify.password.encode('utf-8')).digest().hex() # Hash the new password and modify the column with new password
            db.add(user_model) # Apply changes to the record in the table
            db.commit() # Commit the changes to database