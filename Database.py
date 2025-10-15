from sqlalchemy import create_engine # Import the engine function to define the database engine
from sqlalchemy.orm import sessionmaker # Import the session-maker function to establish a database session
from sqlalchemy.ext.declarative import declarative_base # Import the base function to create the database


database_link:str = 'sqlite:///./user.db' # Link where the SQL database will be located

engine = create_engine(database_link, connect_args={'check_same_thread': False}) # Create the database engine at the link passed to arguments
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Establish a session between the database created and the server
Base = declarative_base() # Construct the base class required to create the database and tables in the database


