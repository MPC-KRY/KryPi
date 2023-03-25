from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hash = Column(String)
    salt = Column(String)
    iteration = Column(Integer)
    email = Column(String)
    totp = Column(Integer)

    def __repr__(self):
        return f"<User(username='{self.username}', hash={self.hash}, totp={self.totp}, email={self.email})>"


class Database:
    def __init__(self, name):
        db_url = 'sqlite:///' + name + '.db'
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def add_user(self, user):
        self.session.add(user)
        try:
            self.session.commit()
            return True
        except IntegrityError as e:
            self.session.rollback()
            return False

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_name(self, username):
        return self.session.query(User).filter_by(username=username).first()

    def get_users(self):
        return self.session.query(User).all()


if __name__ == "__main__":
    db = Database("example")
    print(db.get_users())
    user = User(username='Jasdasde', hash="7384783834", salt="7384783834", iteration=23, totp=20304, email="blahblah@boe.cz")
    db.add_user(user)
    users = db.get_users()
    for user in users:
        print(user)

    print("blah blah")
    print(db.get_user_by_id(1))
    print(db.get_user_by_name("Jasdasde"))
