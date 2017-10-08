from networkx import DiGraph, is_directed_acyclic_graph
from simplyrestful.validators import Validator
from simplyrestful.exceptions import Conflict
from lycheepy.models import Process, Output


class ChainValidator(Validator):
    def validate(self, data):
        steps = data.get('steps', [])
        self._validate_at_least_one_step(steps)
        graph = self._build_digraph(steps)
        self._validate_acyclic(graph)
        self._validate_match(steps, graph)

    def _validate_at_least_one_step(self, steps):
        if not steps:
            raise Conflict('At least one step is required')

    def _validate_acyclic(self, graph):
        if not is_directed_acyclic_graph(graph):
            raise Conflict('Graph must be directed and acyclic')

    def _validate_match(self, steps, graph):
        processes = self._get_chain_processes(graph)
        for process in processes:
            process_identifier = process.identifier
            predecessors = graph.predecessors(process_identifier)
            if predecessors:
                predecessors_outputs = self._get_outpus(predecessors)
                for process_input in process.inputs:
                    input_identifier = process_input.identifier
                    has_match = self._has_match(process_identifier, input_identifier, steps)
                    matchable = self._is_matchable(input_identifier, predecessors_outputs)
                    if not has_match and not matchable:
                        raise Conflict(
                            'The "{}" input of "{}" requires an explicit match, or only one predecessor output with the same identifier'.format(input_identifier, process_identifier)
                        )

    def _has_match(self, process, process_input, steps):
        has = False
        for step in steps:
            if step.get('after') == process:
                for o, i in step.get('match', {}).iteritems():
                    if i == process_input:
                        has = True
        return has

    def _is_matchable(self, process_input, predecessors_outputs):
        count = 0
        for output in predecessors_outputs:
            if output.identifier == process_input:
                count += 1
        return count == 1

    def _get_outpus(self, processes):
        return Output.query.filter(Output.process.has(Process.identifier.in_(processes))).all()

    def _get_chain_processes(self, graph):
        return Process.query.filter(Process.identifier.in_(graph.nodes())).all()

    def _build_digraph(self, steps):
        graph = DiGraph()
        for step in steps:
            self._validate_repeated(graph, step['before'], step['after'])
            graph.add_edge(step['before'], step['after'])
        return graph

    def _validate_repeated(self, graph, before, after):
        nodes = graph.nodes()
        if before in nodes and after in nodes and graph.number_of_edges(before, after):
            raise Conflict('{} to {} step is repeated'.format(before, after))
