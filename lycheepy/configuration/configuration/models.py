from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from simplyrestful.settings import configure_from_module
configure_from_module('settings')

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
    publishables = relationship('Output', secondary='publishable_output')


class Input(Describable):
    __tablename__ = 'input'
    __table_args__ = (UniqueConstraint('process_id', 'identifier'),)
    identifier = Column(Text, nullable=False)
    process_id = Column(Integer, ForeignKey('process.id'))
    process = relationship('Process', backref='inputs')
    format_id = Column(Integer, ForeignKey('format.id'))
    format = relationship('Format')
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    data_type = relationship('DataType')


class Output(Describable):
    __tablename__ = 'output'
    __table_args__ = (UniqueConstraint('process_id', 'identifier'),)
    identifier = Column(Text, nullable=False)
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    process = relationship('Process', backref='outputs')
    format_id = Column(Integer, ForeignKey('format.id'))
    format = relationship('Format')
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    data_type = relationship('DataType')


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


class PublishableOutput(Model):
    __tablename__ = 'publishable_output'
    chain_id = Column(Integer, ForeignKey('chain.id'), primary_key=True)
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


class Format(Model):
    __tablename__ = 'format'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    mime_type = Column(Text, nullable=False, unique=True)
    extension = Column(Text, nullable=False)


class DataType(Model):
    __tablename__ = 'data_type'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)


if __name__ == '__main__':
    Model.metadata.create_all(engine, checkfirst=True)
