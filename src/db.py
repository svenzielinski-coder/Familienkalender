from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    owner = Column(String(80), nullable=False)   # Mama/Papa/Kind1/Kind2/Alle
    notes = Column(Text, nullable=True)

class SpecialDay(Base):
    __tablename__ = "special_days"
    id = Column(Integer, primary_key=True)
    kind = Column(String(40), nullable=False)     # holiday | school_break
    title = Column(String(200), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)        # end exklusiv bei All-Day Events

def get_engine(db_path="calendar.db"):
    return create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )

def get_session(db_path="calendar.db"):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
