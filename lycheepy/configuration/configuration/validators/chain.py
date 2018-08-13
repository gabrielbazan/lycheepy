from networkx import DiGraph, is_directed_acyclic_graph
from simplyrestful.exceptions import Conflict
from simplyrestful.validators import Validator
from models import Process, Output


class ChainValidator(Validator):

    def validate(self, data, instance=None):
        steps = data.get('steps', [])
        ChainValidator.validate_at_least_one_step(steps)
        graph = ChainValidator.build_digraph(steps)
        ChainValidator.validate_acyclic(graph)
        ChainValidator.validate_match(steps, graph)
        ChainValidator.validate_unique(data)

    @staticmethod
    def validate_unique(data):
        identifier = data.get('identifier')
        process = Process.query.filter_by(identifier=identifier).one_or_none()
        if process:
            raise Conflict('Already exists a process with the given identifier')

    @staticmethod
    def validate_at_least_one_step(steps):
        if not steps:
            raise Conflict('At least one step is required')

    @staticmethod
    def validate_acyclic(graph):
        if not is_directed_acyclic_graph(graph):
            raise Conflict('Graph must be directed and acyclic')

    @staticmethod
    def validate_match(steps, graph):
        m = 'The "{}" input of "{}" requires an explicit match, or only one predecessor output with the same identifier'
        processes = ChainValidator.get_chain_processes(graph)
        for process in processes:
            process_identifier = process.identifier
            predecessors = graph.predecessors(process_identifier)
            if predecessors:
                predecessors_outputs = ChainValidator.get_outputs(predecessors)
                for process_input in process.inputs:
                    input_identifier = process_input.identifier
                    has_match = ChainValidator.has_match(process_identifier, input_identifier, steps)
                    matchable = ChainValidator.is_matchable(input_identifier, predecessors_outputs)
                    if not has_match and not matchable:
                        raise Conflict(m.format(input_identifier, process_identifier))

    @staticmethod
    def has_match(process, process_input, steps):
        has = False
        for step in steps:
            if step.get('after') == process:
                for o, i in step.get('match', {}).iteritems():
                    if i == process_input:
                        has = True
        return has

    @staticmethod
    def is_matchable(process_input, predecessors_outputs):
        count = 0
        for output in predecessors_outputs:
            if output.identifier == process_input:
                count += 1
        return count == 1

    @staticmethod
    def get_outputs(processes):
        return Output.query.filter(Output.process.has(Process.identifier.in_(processes))).all()

    @staticmethod
    def get_chain_processes(graph):
        return Process.query.filter(Process.identifier.in_(graph.nodes())).all()

    @staticmethod
    def build_digraph(steps):
        graph = DiGraph()
        for step in steps:
            ChainValidator.validate_repeated(graph, step['before'], step['after'])
            graph.add_edge(step['before'], step['after'])
        return graph

    @staticmethod
    def validate_repeated(graph, before, after):
        nodes = graph.nodes()
        if before in nodes and after in nodes and graph.number_of_edges(before, after):
            raise Conflict('{} to {} step is repeated'.format(before, after))
