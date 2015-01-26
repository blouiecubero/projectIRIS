 # Import the database object (db) from the main application module
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.exc import DatabaseError, IntegrityError
from app.database import Base

class Project(Base):

    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True,autoincrement=True)
    project_name = Column(String(50), unique=True)
    description = Column(Text)

    def __init__(self, project_name=None, description=None):
        self.project_name = project_name
        self.description = description


    # Return object data in easily serializeable format
    @property
    def serialize(self):
        return {
            'id'                : self.id,
            'project_name'      : self.project_name,
            'description'       : self.description,
        }
       