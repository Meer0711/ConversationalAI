from svc.db.psql.models import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)


def get_sql_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
