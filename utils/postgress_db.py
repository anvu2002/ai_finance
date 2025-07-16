# 1. DB_ENGINE
# 2. create_session factory
# 3. context management for gracefully retrieve a db conn from the pool
# , use it, the auto commit or rollback at the end
import sys
from contextlib import contextmanager
from loguru import logger
from configs.config import DATABASE_URL
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class PostgresDB():
    """
    Interactions with PostgreSQL
    """
    DB_ENGINE = None
    
    def __init__(self, 
                 db_name: str = 'ai_finance'):
        self.db_name = db_name
        PostgresDB.init_db_engine(db_name=db_name)
        
        # Get a session from the current DB_ENGINE pool
        Session = sessionmaker(bind=self.DB_ENGINE)
        self.db_session = Session()

    @classmethod
    def init_db_engine(cls, db_name):
        """"
        Init DB ENGINE
        """
        try:
            if cls.DB_ENGINE is None:
                print(f"[+] Init DB ENGINE")
                cls.DB_ENGINE = create_engine(f"{DATABASE_URL}/{db_name}")
            else:
                print(f"[+] DB ENGINE aready init")
        except Exception as e:
            logger.error(f"FAILED to init DB Engine. Error: {e}")
            sys.exit(1)
        
    @contextmanager
    def get_db_session(session):
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
    
    def validate_db_conn(self):
        with PostgresDB.get_db_session(session=self.db_session) as session:
            sql = text("SELECT 1;")
            session.execute(sql)