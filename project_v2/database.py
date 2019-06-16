from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Float, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import random

engine = create_engine('postgresql+psycopg2://aepks:aepks@localhost/aepks', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    rfid_key = Column(Integer, unique=True)
    username = Column(String)
    email = Column(String)
    disabled = Column(Boolean)
    fingerprint = Column(Integer, unique=True)
    # Relatoinship structures
    transactions = relationship('Transaction', back_populates='user')
    role = relationship("Roles", uselist=False, back_populates='user')

    def balance(self):
        return sum([transaction.amount for transaction in self.transactions])

    # Currently only set up for coffee - reference
    # https://docs.sqlalchemy.org/en/13/orm/extensions/mutable.html#establishing-mutability-on-scalar-column-values
    # for adapting the 'price' field of 'Roles' to a dictionary, whihc would allow for an arbitrary number of
    # objects.

    def price(self):
        if self.role:
            return self.role.price
        else:
            for item in session.query(Item).filter_by(name='coffee'):
                return item.price

    def export_history(self):
        file = open(f'{self.username}_{datetime.now()}.csv', 'w+')
        for transaction in self.transactions:
            if transaction.amount < 0:
                type = 'PURCHASE'
            else:
                type = 'CREDIT'
            file.write(f'{id},{transaction.timestamp},{type},{transaction.amount}\n')

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    name = Column(String)
    permissions = Column(Boolean)
    price = Column(Float)
    user = relationship('User', back_populates='role')

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    amount = Column(Float(precision=2))
    user = relationship('User', back_populates='transactions')

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer,primary_key=True)
    name = Column(String,unique=True)
    price = Column(Float(precision=2))

# def return_user(rfid_key):
#     # for user in session.(User).filter_by(rfid_key=rfid_key):
#     #     return user
#
#     new_user = User(rfid_key=rfid_key, username=None,email=None,disabled=0)
#
#     for _ in range(30):
#         new_user.transactions.append(random.randrange(-5,5))
#     session.add(new_user)
#     session.commit()
#     return new_user

def user_balance(user):
    return sum([transaction for transaction in session.query(User.transactions)])


Base.metadata.create_all(engine)


test_user = User(rfid_key=random.randint(11111,55555),disabled=False)
test_user.username="jschmitz2"
test_user.email="jschmtiz2@hawk.iit.edu"
test_user.disabled=True
test_user.transactions.append(Transaction(amount=0.5))

session.add(test_user)

for instance in session.query(User).filter_by(rfid_key=49923):
    print(instance.username)
    print(instance.balance())

session.commit()
