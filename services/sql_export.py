from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float
)

from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class DocumentRecord(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_type = Column(
        String
    )

    document_number = Column(
        String
    )

    document_date = Column(
        String
    )

    total = Column(
        Float
    )


engine = create_engine(
    "sqlite:///./documents.db",
    connect_args={
        "check_same_thread": False
    }
)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(
    bind=engine
)