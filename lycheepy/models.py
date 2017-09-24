from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


from simplyrestful.settings import configure_from_module
configure_from_module('lycheepy.settings')

from simplyrestful.database import engine
from simplyrestful.models.model import Model


class Describable(Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    identifier = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=False)


class Process(Describable):
    __tablename__ = 'process'
    version = Column(Text, nullable=False)
    meta_data = relationship('Metadata', secondary='process_metadata', backref='processes')


class Chain(Describable):
    __tablename__ = 'chain'
    version = Column(Text, nullable=False)
    meta_data = relationship('Metadata', secondary='chain_metadata', backref='chains')


class Input(Describable):
    __tablename__ = 'input'
    __table_args__ = (UniqueConstraint('process_id', 'identifier'),)
    identifier = Column(Text, nullable=False)
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    process = relationship('Process', backref='inputs')


class Output(Describable):
    __tablename__ = 'output'
    __table_args__ = (UniqueConstraint('process_id', 'identifier'),)
    identifier = Column(Text, nullable=False)
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    process = relationship('Process', backref='outputs')


class ExtraOutput(Model):
    __tablename__ = 'extra_output'
    chain_id = Column(Integer, ForeignKey('chain.id'), primary_key=True)
    chain = relationship('Chain', backref='extra_outputs')
    output_id = Column(Integer, ForeignKey('output.id'), primary_key=True)
    output = relationship('Output')


class Execution(Model):
    __tablename__ = 'execution'
    id = Column(Text, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime)
    chain_identifier = Column(Integer, ForeignKey('chain.identifier'), nullable=False)
    chain = relationship('Chain', backref='executions')
    status = Column(Text)

    SUCCESS = 'SUCCESS'
    PROCESSING = 'PROCESSING'
    ERROR = 'ERROR'


class Metadata(Model):
    __tablename__ = 'metadata'
    id = Column(Integer, primary_key=True)
    value = Column(Text, nullable=False)


class ProcessMetadata(Model):
    __tablename__ = 'process_metadata'
    process_id = Column(Integer, ForeignKey('process.id'), primary_key=True)
    metadata_id = Column(Integer, ForeignKey('metadata.id'), primary_key=True)


class ChainMetadata(Model):
    __tablename__ = 'chain_metadata'
    chain_id = Column(Integer, ForeignKey('chain.id'), primary_key=True)
    metadata_id = Column(Integer, ForeignKey('metadata.id'), primary_key=True)


class Step(Model):
    __tablename__ = 'step'
    id = Column(Integer, primary_key=True)
    after_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    after = relationship('Process', foreign_keys=after_id)
    before_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    before = relationship('Process', foreign_keys=before_id)
    chain_id = Column(Integer, ForeignKey('chain.id'), nullable=False)
    chain = relationship('Chain', backref='steps')
    publishables = relationship('Output', secondary='publishable_output')


class PublishableOutput(Model):
    __tablename__ = 'publishable_output'
    step_id = Column(Integer, ForeignKey('step.id'), primary_key=True)
    output_id = Column(Integer, ForeignKey('output.id'), primary_key=True)


class StepMatch(Model):
    __tablename__ = 'step_match'
    id = Column(Integer, primary_key=True)
    input_id = Column(Integer, ForeignKey('input.id'), nullable=False)
    input = relationship('Input')
    output_id = Column(Integer, ForeignKey('output.id'), nullable=False)
    output = relationship('Output')
    step_id = Column(Integer, ForeignKey('step.id'), nullable=False)
    step = relationship('Step', backref='matches')


if __name__ == '__main__':
    Model.metadata.create_all(engine, checkfirst=True)
