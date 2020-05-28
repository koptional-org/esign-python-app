from main import app, get_db


def init_db():
    with app.app_context():
        db = get_db()
        qry = open('schema.sql', 'r').read()
        c = db.cursor()
        c.executescript(qry)
        db.commit()
        c.close()
        db.close()


if __name__ == "__main__":
    init_db()
