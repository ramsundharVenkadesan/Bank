from fastapi import FastAPI # Import Fast-API class to start up the server
from Database import engine # Import database engine to create the database and tables in the database
import Tables # Import tables in the database
from API_Operations import router_object # Import the router to create a path to the API file
from Authentication import router # Import the router to create a path to the Authentication file


application:FastAPI = FastAPI() # Create an instance to FastAPI class to start the server
application.include_router(router) # Include the router object of the Authentication operations
application.include_router(router_object) # Include the router object imported for API operations

Tables.Base.metadata.create_all(bind=engine) # Create all the tables defined in the file based on the engine passed to the arguments