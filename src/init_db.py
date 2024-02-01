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

def populate(session):
    # User 1
    user1 = User(
        username='User1',
        password='123',
        public_key='keys/users/User1/public_key.pem',
    )
    session.add(user1)

    # Document 1 for User 1
    with open('intro/outputs/doc1_user1_protected', 'r') as file:
        document1json = json.load(file)

    document1 = Document(
        restaurant_name="Burger_King",
        protected_document=json.dumps(document1json),
        restaurant_public_key='keys/restaurants/Burger_King/public_key.pem',
        user=user1
    )
    session.add(document1)

    # Document 2 for User 1
    with open('intro/outputs/doc2_user1_protected', 'r') as file:
        document2json = json.load(file)

    document2 = Document(
        restaurant_name="McDonalds",
        protected_document=json.dumps(document2json),
        restaurant_public_key='keys/restaurants/McDonalds/public_key.pem',
        user=user1
    )
    session.add(document2)

    # Document 3 for User 1
    with open('intro/outputs/doc3_user1_protected', 'r') as file:
        document3json = json.load(file)

    document3 = Document(
        restaurant_name="KFC",
        protected_document=json.dumps(document3json),
        restaurant_public_key='keys/restaurants/KFC/public_key.pem',
        user=user1
    )
    session.add(document3)

    # User 2
    user2 = User(
        username='User2',
        password='123',
        public_key='keys/users/User2/public_key.pem',
    )
    session.add(user2)

    document1_user2 = Document(
        restaurant_name="Burger_King",
        restaurant_public_key='keys/restaurants/Burger_King/public_key.pem',
        user=user2
    )
    session.add(document1_user2)

    document2_user2 = Document(
        restaurant_name="McDonalds",
        restaurant_public_key='keys/restaurants/McDonalds/public_key.pem',
        user=user2
    )
    session.add(document2_user2)

    document3_user2 = Document(
        restaurant_name="KFC",
        restaurant_public_key='keys/restaurants/KFC/public_key.pem',
        user=user2
    )
    session.add(document3_user2)

    # User 3
    user3 = User(
        username='User3',
        password='123',
        public_key='keys/users/User3/public_key.pem',
    )
    session.add(user3)

    document1_user3 = Document(
        restaurant_name="Burger_King",
        restaurant_public_key='keys/restaurants/Burger_King/public_key.pem',
        user=user3
    )
    session.add(document1_user3)


    document2_user3 = Document(
        restaurant_name="McDonalds",
        restaurant_public_key='keys/restaurants/McDonalds/public_key.pem',
        user=user3
    )
    session.add(document2_user3)

    document3_user3 = Document(
        restaurant_name="KFC",
        restaurant_public_key='keys/restaurants/KFC/public_key.pem',
        user=user3
    )
    session.add(document3_user3)

    session.commit()



if __name__ == "__main__":
    populate(dbsession)