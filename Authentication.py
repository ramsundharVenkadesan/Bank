from Tables import User # Import the User table
from fastapi import APIRouter, Depends, HTTPException, Query # Import multiple classes from Fast-API package
from starlette import status # Import the status class to retrieve HTTP status codes
from typing import Annotated # Import Annotated class to establish dependencies
from Database import LocalSession # Import the LocalSession variable that contains the Session-Maker instance
from sqlalchemy.orm import Session # Import Session class to establish a session between database and server
from pydantic import BaseModel, Field # Import BaseModel and Field classes for data validation
from hashlib import sha512 # Import SHA-512 hashing algorithm
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # Import O-Auth token-bearer and request form classes to store and accept credentials
from jose import jwt, JWTError # Import JASON Web Token (JWT) class and Error related to JWT
from datetime import datetime, timedelta, timezone # Import Time, Date, and Timezone
from Crypto.Random import get_random_bytes # Import function to generate random bytes

secret_key = get_random_bytes(32) # Retrieve 32 random bytes which becomes secret
oauth2_bearer:OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="Authentication/login") # Create an instance of bearer token to accept client tokens


router:APIRouter = APIRouter(
    prefix = '/Authentication', # A new path for any authentication operations
    tags = ['Authentication'] # Tags to separate operations
) # API Router instance to establish a path between this module and the main file

class Token(BaseModel): # Token Request class that inherits BaseModel for data validation
    access_token: str # Store the token itself
    token_type: str # Store token type (JWT)


def database_connection() -> Session: # Function to establish connection to the database
    connection = LocalSession() # Establish a local session to the database
    try: yield connection # Hold the connection using yield-keyword until the response is sent
    finally: connection.close() # Close the connection once the response has been sent

db_dependency = Annotated[Session, Depends(database_connection)] # Dependency injection that waits for the Session is established by the function
oauth_dependency = Annotated[OAuth2PasswordRequestForm, Depends()] # Dependency inject that waits for the client to populate the request form
bearer_dependency = Annotated[str, Depends(oauth2_bearer)] # Dependency inject that waits for bearer token to accept the token and return relevant information as a string

class UserRequest(BaseModel): # Request class that inherits from Base-Model for data validation
    first_name:str = Field(min_length=1, max_length=50) # Field instance to set limits and constraints on input passed by client
    last_name:str = Field(min_length=1, max_length=50) # Field instance to set limits and constraints on input passed by client
    email:str = Field(min_length=1, max_length=50) # Field instance to set limits and constraints on input passed by client
    username:str = Field(min_length=1, max_length=50) # Field instance to set limits and constraints on input passed by client
    password:str = Field(min_length=1, max_length=50) # Field instance to set limits and constraints on input passed by client
    SSN:str = Field(min_length=9, max_length=9) # Field instance to set limits and constraints on input passed by client

    model_config = { # Configuration to set example values
        'json_schema_extra': { # JSON Schema
            'example': { # Example data
                'first_name': 'John', 'last_name': 'Doe', 'email': 'johnDoe@none.com', # Placeholders for user input
                'username': 'johnDoe', 'password': 'Password', 'SSN': '123456789' # Placeholders for user input
            }
        }
    }

def verification(username:str, password:str, db:db_dependency): # Function to verify password
    user_record = db.query(User).filter(User.username == username).first() # Query the database to retrieve first record with the matching username
    if user_record is not None: # Record found in database
        hashed_password = sha512(password.encode('utf-8')).digest().hex() # Use SHA-512 to hash the password passed to the function and retrieve the hexadecimal version
        if user_record.hashed_password == hashed_password: return user_record # The hashed password stored in the record within the table matches the password passed to the function, thus record is returned back
        else: return False # The password passed to function and password stored in table do not match
    else: return False # The record was not found in database

def create_access_token(username:str, ssn:str, expires_delta:timedelta): # Function to create a JSON token
    encode:dict[str, str] = {'sub': username, 'id': ssn} # Payload part of the token (Second part) to identify the JWT
    time_now = datetime.now(timezone.utc) + expires_delta # Retrieve the current time and add it to the expiration time to specify how long the token is valid for
    encode.update({'exp': time_now}) # Add entry to the payload dictionary
    return jwt.encode(encode, secret_key, algorithm='HS256') # Base64 encode the payload with the secret key and SHA-256 algorithm

@router.post('/create_user', status_code=status.HTTP_201_CREATED) # POST Request to create a record with a 201 OK response if successful to indicate record was added to database
async def create_user(db:db_dependency, user:UserRequest): # Accept the Session connection to the database and UserRequest instance as an argument
    user = User( # Create User record instance
        first_name=user.first_name, # Key-word argument to set first-name column with data set on the request-class instance by the user
        last_name=user.last_name, # Key-word argument to set last-name column with data set on the request-class instance by the user
        email=user.email, # Key-word argument to set email column with data set on the request-class instance by the user
        username=user.username, # Key-word argument to set username column with data set on the request-class instance by the user
        hashed_password=sha512(user.password.encode('utf-8')).digest().hex(), # Key-word argument to set password column by hashing (SHA 512 algorithm) the password set by the user on the request-instance
        SSN=user.SSN # Key-word argument to set SSN column with data set on the request-class instance by the user
    )
    db.add(user) # Add record to the table
    db.commit() # Commit changes to the database

@router.get('/get_user', status_code=status.HTTP_200_OK) # GET Request to retrieve all users from the database with a 200 OK response if successful
async def get_user(db:db_dependency): return db.query(User).all() # Query the User table and retrieve all the records

@router.get('/get_user/', status_code=status.HTTP_200_OK) # GET Request to retrieve a record based on the SSN-ID passed as dynamic parameter with a 200 OK response if successful
async def get_SSN(db:db_dependency, ssn_input=Query(min_length=9, max_length=9)): # Accept the Session connection to the database and Query parameter that must be 9 digits long
    record = db.query(User).filter(User.SSN == ssn_input).first() # Query the User table, filter the table to retrieve the record that matches the SSN passed, and return the first record with matching SSN
    if record is not None: return record # Record found in table that is returned
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") # Raise HTTP-Exception to indicate record was not found (404)

@router.post('/login', response_model=Token) # POST Request to create a record with a response being a token-class
async def login(db:db_dependency, form:oauth_dependency): # Accept the Session connection to database and request form
    user_record = verification(form.username, form.password, db) # Verify the username and password entered into the form by the user
    if not user_record: # User record not found
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password') # Raise HTTP-Exception to indicate user is not authorized (401)
    else: # User record was found
        token = create_access_token(user_record.username, user_record.SSN, expires_delta=timedelta(minutes=30)) # Create a JWT token that is valid for 30 minutes from now
        return {'access_token': token, 'token_type': 'Bearer'} # Return the token that was Base64 encoded (Header.Payload.Signature) and type

async def get_current_user(token:bearer_dependency): # Function that accepts the token sent by the client
    try: # Try clause
        payload:dict = jwt.decode(token, secret_key, algorithms=['HS256']) # Decode the payload on token with the secret and algorithm used to encode it (returned as dictionary)
        username:str = payload.get('sub') # Retrieve the subject from the payload
        ssn:str = payload.get('id') # Retrieve the SSN from the payload
        if username is None or ssn is None: # If either the subject or ID is not available
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Cannot Validate Credentials') # Raise HTTP-Exception to indicate user is not authorized (401) because it cannot be validated
        else: return {'Username': username, 'SSN': ssn} # Return the username and SSN information from the decoded payload as a dictionary
    except JWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Cannot Validate Credentials') # Catch JWT error because it cannot be decoded
