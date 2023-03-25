from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String)
    totp = Column(Integer)
    devices = relationship('Device', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"<User(username='{self.username}', password={self.password}, totp={self.totp}, email={self.email})>"


class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    public_key = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    def __repr__(self):
        return f"<User(public_key='{self.public_key}', user_id={self.user_id})>"


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

    def add_device_to_user(self, username, device):
        user = self.get_user_by_name(username)
        user.devices.append(device)
        self.session.add(user)
        return self.save_changes()

    def save_changes(self):
        try:
            self.session.commit()
            return True
        except SQLAlchemyError as ex:
            self.session.rollback()
            return False

if __name__ == "__main__":
    db = Database("example")
    print(db.get_users())
    user = User(username='Jasdasde', password="7384783834", totp=20304, email="blahblah@boe.cz")
    device = Device(public_key="77382")
    db.add_device_to_user("Jasdasde", device)
    db.save_changes()
    db.add_user(user)
    users = db.get_users()
    for user in users:
        print(user)

    print("blah blah")
    print(db.get_user_by_id(1))
    print(db.get_user_by_name("Jasdasde"))
    print(db.get_user_by_id(1).devices.all())
