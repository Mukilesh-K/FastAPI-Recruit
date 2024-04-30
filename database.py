import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, insert, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSON
import yaml
import logging
from Logging import setup_logging  # Import centralized logging setup

# Initialize logger
logger = setup_logging()

base = declarative_base()

class MaayuInsights(base):
    __tablename__ = 'maayu_insights'
    applicant_id = Column(String, primary_key=True)
    resume = Column(Text, nullable=False)
    job_description = Column(Text, nullable=False)
    request_timestamp = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    resume_entities = Column(Text, nullable=True)
    jd_entities = Column(Text, nullable=True)
    insights = Column(Text, nullable=True)
    response_timestamp = Column(DateTime, nullable=True)


class MaayuErrors(base):
    __tablename__ = 'maayu_errors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(String, nullable=True)
    error = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


def get_connection():
    """
    This function is used to create DB connection
    :return: Success - connection engine, True, Failure - error, False
    """
    try:
        with open("config.yaml", 'r') as stream:
            config = yaml.safe_load(stream)
            db_config = config.get('database', {})
            user = db_config.get('user')
            password = db_config.get('password')
            host = db_config.get('host')
            port = db_config.get('port')
            database = db_config.get('database_name')
        engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
        conn = engine.connect()
        conn.close()
        return engine, True
    except Exception as error:
        logger.error(f"Error connecting to database: {error}")
        return error, False


def create_tables(table_names: list):
    """
    Used to create tables in DB if tables are not present
    :param table_names: list - name of tables to be created mentioned in config
    :return: None
    """
    try:
        engine, status = get_connection()
        if status is False:
            raise Exception(f"Unable to connect to DB - {engine}")
        present_flag = True
        for table in table_names:
            if not sqlalchemy.inspect(engine).has_table(table):
                present_flag = False
        if present_flag is False:
            logger.info("Creating all required tables in database")
            base.metadata.create_all(engine)
        engine.dispose()
    except Exception as error:
        logger.error(f"Error creating tables: {error}")


def insert_query(table_class, insert_list):
    """
    Used to execute SQL insert statement
    :param table_class: object - object of the table class on which insert statement is run
    :param insert_list: list of statement to be executed, multiple statements could be sent in a list
    :return: None
    """
    try:
        engine, status = get_connection()
        if status is False:
            raise Exception(f"Unable to connect to DB - {engine}")
        conn = engine.connect()
        trans = conn.begin()
        conn.execute(insert(table_class).values(insert_list))
        trans.commit()
        conn.close()
    except Exception as error:
        logger.error(f"Error inserting values into table: {error}")


def select_query(statement):
    """
    Used to run select query and fetch results from DB
    :param statement: string - select query statement
    :return: list - fetched data points from DB
    """
    try:
        engine, status = get_connection()
        if status is False:
            raise Exception(f"Unable to connect to DB - {engine}")
        conn = engine.connect()
        fetched_results = conn.execute(statement)
        conn.close()
        return fetched_results
    except Exception as error:
        logger.error(f"Error fetching values from table: {error}")


def update_query(statement):
    """
    Used to update a row in DB
    :param statement: string - update query statement
    :return: None
    """
    try:
        engine, status = get_connection()
        if status is False:
            raise Exception(f"Unable to connect to DB - {engine}")
        conn = engine.connect()
        trans = conn.begin()
        conn.execute(statement)
        trans.commit()
        conn.close()
    except Exception as error:
        logger.error(f"Error updating table: {error}")

# Uncomment and use these functions as needed

# s = select(Maintable.resume, Maintable.job_description).where(Maintable.id == 2)
# result = select_query(s)
# for r in result:
#     print(r.job_description)

# create_tables(["analysis", "error_table"])

# update_query(update(Maintable).where(Maintable.id == 1).values(status='processing'))
