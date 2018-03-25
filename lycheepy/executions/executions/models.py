from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from simplyrestful.settings import configure_from_module
configure_from_module('settings')

from simplyrestful.database import engine
from simplyrestful.models.model import Model


class ExecutionStatus(Model):
    __tablename__ = 'execution_status'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)


class Execution(Model):
    __tablename__ = 'execution'
    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False, default=datetime.utcnow)
    end = Column(DateTime)
    chain_identifier = Column(Text, nullable=False)
    execution_id = Column(Text, nullable=False)
    reason = Column(Text)
    status_id = Column(Integer, ForeignKey('execution_status.id'), nullable=False)
    status = relationship('ExecutionStatus')


if __name__ == '__main__':
    Model.metadata.create_all(engine, checkfirst=True)
