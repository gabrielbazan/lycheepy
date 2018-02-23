from pywps.app.Common import Metadata

from networkx import DiGraph

from utils import DefaultDict
from service import ProcessesGateway
from chaining.chain import Chain
from chaining.anti_chains import AntiChainsBuilder


class ChainBuilder(object):
    def __init__(self, model):
        self.model = model
        self.graph = self.__build_graph()

    def build(self):
        return Chain(
            self.model.get('identifier'),
            self.model.get('title'),
            self._build_metadata(),
            self._build_inputs(),
            self._build_outputs(),
            self._build_anti_chains(),
            self._build_predecessors(),
            self._build_successors(),
            self._build_match(),
            self._build_products(),
            abstract=self.model.get('abstract'),
            version=self.model.get('version')
        )

    def _build_metadata(self):
        return [Metadata(metadata) for metadata in self.model.get('metadata')]

    def _build_inputs(self):
        return [
            process_input
            for process in self.__get_nodes_without_predecessors()
            for process_input in ProcessesGateway.get(process).inputs
        ]

    def _build_outputs(self):
        return [
            process_output
            for process in self.__get_nodes_without_successors()
            for process_output in ProcessesGateway.get(process).outputs
        ]

    def _build_anti_chains(self):
        return AntiChainsBuilder(self.graph).build()

    def _build_predecessors(self):
        return {
            node: self.graph.predecessors(node)
            for node in self.graph.nodes()
        }

    def _build_successors(self):
        return {
            node: self.graph.successors(node)
            for node in self.graph.nodes()
        }

    def _build_match(self):
        matches = DefaultDict()
        for step in self.model.get('steps'):
            before = step.get('before')
            after = step.get('after')
            for output, process_input in step.get('match').iteritems():
                matches[after][before][output] = process_input
        return matches

    def _build_products(self):
        return {
            process: outputs
            for process, outputs in self.model.get('publish').iteritems()
        }

    def __build_graph(self):
        g = DiGraph()
        for step in self.model.get('steps'):
            g.add_edge(step.get('before'), step.get('after'))
        return g

    def __get_nodes_without_predecessors(self):
        return [node for node, degree in self.graph.in_degree_iter() if degree is 0]

    def __get_nodes_without_successors(self):
        return [node for node, degree in self.graph.in_degree_iter() if len(self.graph.successors(node)) is 0]
