import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

Base = declarative_base()


def _get_database_url():
    """Build database URL from environment variables."""
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    user = os.getenv('POSTGRES_USER', 'campus')
    password = os.getenv('POSTGRES_PASSWORD', 'campus_dev_2026')
    db_name = os.getenv('POSTGRES_DB', 'campus_platform')
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


class Database:
    """Database manager with connection pooling."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.engine = create_engine(
            _get_database_url(),
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=os.getenv('FLASK_ENV') == 'development',
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        """Create a new database session."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def init_db(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)


# Module-level convenience objects
db = Database()
get_session = db.get_session
init_db = db.init_db
