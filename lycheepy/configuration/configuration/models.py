from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from simplyrestful.settings import configure_from_module
configure_from_module('settings')

from simplyrestful.database import engine
from simplyrestful.models.model import Model

from networkx import DiGraph


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

    @property
    def chains(self):
        steps = self.steps_before + self.steps_after
        return [step.chain for step in steps]


class Chain(Describable):
    __tablename__ = 'chain'
    version = Column(Text, nullable=False)
    meta_data = relationship('Metadata', secondary='chain_metadata', backref='chains')
    publishables = relationship('Output', secondary='publishable_output')

    @property
    def graph(self):
        graph = DiGraph()
        for step in self.steps:
            graph.add_edge(step.before.identifier, step.after.identifier)
        return graph

    @property
    def inputs(self):
        processes = [node for node, degree in self.graph.in_degree_iter() if degree is 0]
        return Input.query.filter(Input.process.has(Process.identifier.in_(processes))).all()

    @property
    def outputs(self):
        processes = [node for node, degree in self.graph.in_degree_iter() if len(self.graph.successors(node)) is 0]
        return Output.query.filter(Output.process.has(Process.identifier.in_(processes))).all()


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
    after = relationship('Process', foreign_keys=after_id, backref='steps_after')
    before_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    before = relationship('Process', foreign_keys=before_id, backref='steps_before')
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


# REPOSITORIES TABLES

class RepositoryType(Model):
    __tablename__ = 'repository_type'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

    GEO_SERVER = 'GEO_SERVER'
    FTP = 'FTP'


class RepositorySetting(Model):
    __tablename__ = 'repository_setting'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

    HOST = 'host'
    USERNAME = 'username'
    PASSWORD = 'password'
    TIMEOUT = 'timeout'
    PROTOCOL = 'protocol'
    PORT = 'port'
    PATH = 'path'
    WORKSPACE = 'workspace'


class RepositoryTypeSetting(Model):
    __tablename__ = 'repository_type_setting'
    __table_args__ = (UniqueConstraint('type_id', 'setting_id'),)
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('repository_type.id'), nullable=False)
    type = relationship('RepositoryType', backref='type_settings')
    setting_id = Column(Integer, ForeignKey('repository_setting.id'), nullable=False)
    setting = relationship('RepositorySetting')
    mandatory = Column(Boolean, nullable=False, default=False)


class Repository(Model):
    __tablename__ = 'repository'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    created = Column(DateTime, default=func.now())
    enabled = Column(Boolean, nullable=False, default=True)
    deleted = Column(Boolean, nullable=False, default=False)
    type_id = Column(Integer, ForeignKey('repository_type.id'), nullable=False)
    type = relationship('RepositoryType', backref='repositories')


class RepositoryConfiguration(Model):
    __tablename__ = 'repository_configuration'
    repository_id = Column(Integer, ForeignKey('repository.id'), primary_key=True)
    repository = relationship('Repository', backref='configurations')
    type_setting_id = Column(Integer, ForeignKey('repository_type_setting.id'), primary_key=True)
    type_setting = relationship('RepositoryTypeSetting')
    value = Column(Text)


if __name__ == '__main__':
    Model.metadata.create_all(engine, checkfirst=True)
