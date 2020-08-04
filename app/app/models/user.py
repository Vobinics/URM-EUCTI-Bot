from sqlalchemy import Column, BigInteger, String, Integer, sql

from . import db


class User(db.Model):
    __tablename__ = 'users'
    query: sql.Select

    id: Column = Column(BigInteger, primary_key=True)
    normal_distance: Column = Column(Integer)
    normal_speed: Column = Column(Integer)
    place_residence: Column = Column(String(255))
