import json
from datetime import datetime

import networkx as nx
from pywps.app.Common import Metadata

from simplyrestful.database import session

from lycheepy.utils import DefaultDict
from lycheepy.models import Execution
from lycheepy.wps.chaining.publisher_process import PublisherProcess
from lycheepy.wps.chaining.distribution.broker import run_process
from lycheepy.wps.chaining.distribution.serialization import OutputsSerializer


class Chain(PublisherProcess):

    def __init__(self, model, processes):

        self.processes = processes

        self.model = model

        self.graph = nx.DiGraph()
        self.match = DefaultDict()
        self.products = dict()

        self.outputs_data = dict()

        self.build_graph()

        self.execution = None

        super(Chain, self).__init__(
            self._handle,
            self.model.identifier,
            self.model.title,
            abstract=self.model.abstract,
            inputs=self.get_inputs(),
            outputs= self.get_outputs(),
            version=self.model.version,
            metadata=[Metadata(metadata.value) for metadata in self.model.meta_data],

            # Check if all the involved processes support it?
            # Or only the ones that provide the chain outputs?
            store_supported=True,

            status_supported=True
        )

    def get_inputs(self):
        inputs = []
        for p in self.get_nodes_without_predecessors():
            inputs.extend(self.processes[p].inputs)
        return inputs

    def get_outputs(self):
        outputs = []

        for process in self.get_nodes_without_successors():
            process_outputs = self.processes[process].outputs
            outputs.extend(process_outputs)
            self.outputs_data[process] = [output.identifier for output in process_outputs]

        for output_data in self.model.extra_outputs:
            process = output_data.process.identifier
            output = output_data.identifier

            process_outputs = {o.identifier: o for o in self.processes[process].outputs}

            outputs.append(process_outputs[output])

            if process not in self.outputs_data:
                self.outputs_data[process] = []
            self.outputs_data[process].append(output)

        return outputs

    def get_nodes_without_predecessors(self):
        return [node for node, degree in self.graph.in_degree_iter() if degree is 0]

    def get_nodes_without_successors(self):
        return [node for node, degree in self.graph.in_degree_iter() if len(self.graph.successors(node)) is 0]

    def build_graph(self):
        for step in self.model.steps:
            before = step.before.identifier
            after = step.after.identifier

            self.graph.add_edge(before, after)

            for match in step.matches:
                output = match.output.identifier
                input = match.input.identifier
                self.match[after][before][output] = input

            for output in step.publishables:
                process = output.process.identifier
                if process not in self.products:
                    self.products[process] = []
                self.products[process].append(output.identifier)

    def get_anti_chain(self):
        anti_chain = [a[0] if len(a) == 1 else a for a in list(nx.antichains(self.graph))]
        anti_chain.pop(0)

        return list(
            reversed(
                [
                    a for a in anti_chain
                    if a not in [
                        c for b in anti_chain
                        if type(b) is list
                        for c in b
                    ]
                ]
            )
        )

    def _handle(self, wps_request, wps_response):
        outputs = dict()

        self._begin_execution()

        for level in self.get_anti_chain():
            results = dict()

            request_json = json.loads(wps_request.json)

            level = level if type(level) is list else [level]

            if len(level) == 1:  # 0 ???
                process = level[0]
                outputs[process] = self.run_process(process, request_json, outputs, async=False)
            else:
                for process in level:
                    results[process] = self.run_process(process, request_json, outputs, async=True)

                for process in level:
                    outputs[process] = results[process].get(30)  # TODO: Timeout config in seconds

            # Publish. TODO: Define where it should be done. In the celery task?
            # Yes. In the Celery task, to run publication in paralel
            for process in level:
                self.publish(process, outputs[process])

        self.set_outputs_values(wps_response, outputs)

        self._end_execution()

        return wps_response

    def _begin_execution(self):
        self.execution = Execution(chain=self.model, id=self.uuid, status=Execution.PROCESSING)
        session.add(self.execution)

    def _end_execution(self):
        self.execution.status = Execution.SUCCESS
        self.execution.end = datetime.now()
        session.add(self.execution)

    def run_process(self, process, request_json, outputs, async=False):
        request_json['identifiers'] = [process]

        if process not in self.get_nodes_without_predecessors():
            request_json['inputs'] = self.get_process_inputs(outputs, process)

        if async:
            return run_process.delay(process, json.dumps(request_json))
        else:
            return run_process(process, json.dumps(request_json))

    def get_process_inputs(self, outputs, p):
        inputs = {}
        for s in self.graph.predecessors(p):
            for k, output in outputs[s].iteritems():
                input_name = self.match[p][s][k] if k in self.match[p][s] else k
                inputs[input_name] = output
        return inputs

    def set_outputs_values(self, wps_response, execution_outputs):
        for process, outputs in self.outputs_data.iteritems():
            for output in outputs:
                # TODO: Handle outputs with multiple occurrences
                OutputsSerializer.add_data(
                    execution_outputs[process][output][0],
                    wps_response.outputs[output]
                )

    def publish(self, process, outputs):
        m = {
            'application/x-ogc-wcs; version=2.0': 'publish_raster',
            'application/gml+xml': 'publish_features'
        }
        if process in self.products:
            for product in self.products[process]:
                for output in outputs[product]:
                    mime_type = output['data_format']['mime_type']
                    if mime_type in m:
                        product_identifier = '{}:{}:{}'.format(process, self.uuid, product)
                        getattr(self.get_repository(), m[mime_type])(
                            self,
                            product_identifier,
                            output['file']
                        )

    # TODO: Chain class should be abstract? And implement this method in child classes
    def get_repository(self):
        from publishing.geo_server_repository import GeoServerRepository
        return GeoServerRepository()
