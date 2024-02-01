import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Text, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users_info'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    public_key = Column(String)
    documents = relationship('Document', backref='user')  # One-to-many relationship with Document

class Document(Base):
    __tablename__ = 'documents_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users_info.id'))  # Foreign key referencing the users_info table
    restaurant_name = Column(String)
    protected_document = Column(Text)
    restaurant_public_key = Column(String)
    review = Column(Text, nullable=True)
    review_signature = Column(String, nullable=True)

db_username = 'postgres'
db_password = 'postgres'
db_host = '192.168.0.100:5432'
db_name = 'bombappetit'

# Construct the PostgreSQL connection string
postgres_url = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
engine = create_engine(postgres_url, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
dbsession = Session()