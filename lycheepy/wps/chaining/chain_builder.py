from pywps.app.Common import Metadata

import networkx as nx

from lycheepy.utils import DefaultDict
from lycheepy.wps.service import ProcessesGateway
from lycheepy.wps.chaining.chain import Chain
from lycheepy.wps.chaining.anti_chains import AntiChainsBuilder


class ChainBuilder(object):
    def __init__(self, model):
        self.model = model
        self.graph = self.__build_graph()

    def build(self):
        return Chain(
            self.model.identifier,
            self.model.title,
            self._build_metadata(),
            self._build_inputs(),
            self._build_outputs(),
            self._build_anti_chains(),
            self._build_predecessors(),
            self._build_successors(),
            self._build_match(),
            self._build_products(),
            abstract=self.model.abstract,
            version=self.model.version
        )

    def _build_metadata(self):
        return [Metadata(metadata.value) for metadata in self.model.meta_data]

    def _build_inputs(self):
        return [
            process_input
            for process in self.__get_nodes_without_predecessors()
            for process_input in ProcessesGateway.get(process).inputs
        ]

    def _build_outputs(self):
        # TODO: Add extra-outputs
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
        match = DefaultDict()
        for step in self.model.steps:
            before = step.before.identifier
            after = step.after.identifier
            for match in step.matches:
                output = match.output.identifier
                input_identifier = match.input.identifier
                match[after][before][output] = input_identifier
        return match

    def _build_products(self):
        products = dict()
        for step in self.model.steps:
            for output in step.publishables:
                process = output.process.identifier
                if process not in products:
                    products[process] = []
                products[process].append(output.identifier)
        return products

    def __build_graph(self):
        g = nx.DiGraph()
        for step in self.model.steps:
            g.add_edge(step.before.identifier, step.after.identifier)
        return g

    def __get_nodes_without_predecessors(self):
        return [node for node, degree in self.graph.in_degree_iter() if degree is 0]

    def __get_nodes_without_successors(self):
        return [node for node, degree in self.graph.in_degree_iter() if len(self.graph.successors(node)) is 0]
