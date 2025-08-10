from core.db.session import engine
from core.db.models.books import Cards
from sqlalchemy.orm import Session

def init_db():
    with Session(engine) as db:
        if db.query(Cards).count() == 0:
            cards_data = [
                Cards(id="245781"),
                Cards(id="357192"),
                Cards(id="468230"),
                Cards(id="589314"),
                Cards(id="712538"),
                Cards(id="000001")
            ]
            db.add_all(cards_data)
            db.commit() 