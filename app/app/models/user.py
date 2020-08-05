from sqlalchemy import Column, BigInteger, ARRAY, String, Integer, sql

from . import db


class User(db.Model):
    __tablename__ = 'users'
    query: sql.Select

    id: Column = Column(BigInteger, primary_key=True)
    normal_distance: Column = Column(Integer)
    normal_speed: Column = Column(Integer)
    place_residence: Column = Column(String(255))
    done_tasks: Column = Column(ARRAY(Integer), default=list)
    proceed_task: Column = Column(Integer)
