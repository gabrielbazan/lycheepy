from networkx import DiGraph
from utils import DefaultDict
from chain import Chain
from anti_chains import AntiChainsBuilder


class ChainBuilder(object):

    def __init__(self, model):
        self.model = model
        self.graph = self._build_graph()

    def build(self):
        return Chain(
            self.model.get('identifier'),
            self._build_anti_chains(),
            self._build_predecessors(),
            self._get_nodes_without_predecessors(),
            self._get_nodes_without_successors(),
            self._build_match(),
            self._build_products()
        )

    def _build_anti_chains(self):
        return AntiChainsBuilder(self.graph).build()

    def _build_predecessors(self):
        return {
            node: self.graph.predecessors(node)
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

    def _build_graph(self):
        g = DiGraph()
        for step in self.model.get('steps'):
            g.add_edge(step.get('before'), step.get('after'))
        return g

    def _get_nodes_without_predecessors(self):
        return [node for node, degree in self.graph.in_degree_iter() if degree is 0]

    def _get_nodes_without_successors(self):
        return [node for node, degree in self.graph.in_degree_iter() if len(self.graph.successors(node)) is 0]
