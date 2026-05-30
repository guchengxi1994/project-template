from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app_config import get_config

engine = None
SessionLocal = None


def init_db():
    global engine, SessionLocal
    config = get_config()
    engine = create_engine(config.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with engine.begin() as connection:
        connection.execute(text(
            """
            CREATE TABLE IF NOT EXISTS app_heartbeat_log (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                source VARCHAR(64) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ))


def record_heartbeat(source: str):
    if engine is None:
        return
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO app_heartbeat_log (source) VALUES (:source)"),
            {"source": source},
        )

