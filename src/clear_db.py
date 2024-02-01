from sqlalchemy import create_engine, MetaData

# Create a SQLite database file or connect to an existing one
db_username = 'postgres'
db_password = 'postgres'
db_host = '192.168.0.100:5432'
db_name = 'bombappetit'

# Construct the PostgreSQL connection string
postgres_url = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
engine = create_engine(postgres_url, echo=True)

metadata = MetaData()
metadata.reflect(bind=engine)

metadata.drop_all(engine)