import json
from settings import PROCESS_EXECUTION_TIMEOUT


class Chain(object):

    def __init__(self, identifier, anti_chains, predecessors, without_predecessors, without_successors, match, products):
        self.identifier = identifier
        self.anti_chains = anti_chains
        self.predecessors = predecessors
        self.without_predecessors = without_predecessors
        self.without_successors = without_successors
        self.match = match
        self.products = products

    def execute(self, broker, request, execution_id):
        outputs = dict()

        for level in self.anti_chains:
            processes = level if type(level) is list else [level]
            self._load_outputs(
                broker.run_processes(
                    self._get_execution_group(
                        processes, request, outputs, execution_id
                    )
                ).get(PROCESS_EXECUTION_TIMEOUT),
                outputs
            )

        chain_outputs = {
            output_identifier: process_output
            for process_identifier, process_outputs in outputs.iteritems()
            for output_identifier, process_output in process_outputs.iteritems()
            if process_identifier in self.without_successors
        }

        return chain_outputs

    def _get_execution_group(self, processes, wps_request, outputs, execution_id):
        group = dict()
        for process in processes:
            request_json = json.loads(wps_request.json)
            request_json['identifiers'] = [process]
            request_json['inputs'] = self._get_process_inputs(process, request_json, outputs)
            group[process] = dict(
                request=request_json,
                products=self._get_process_products(process),
                chain_identifier=self.identifier,
                execution_id=execution_id
            )
        return group

    def _get_process_products(self, process):
        return self.products[process] if process in self.products else []

    def _get_process_inputs(self, process, request_json, outputs):
        inputs = request_json['inputs']
        if process not in self.without_predecessors:
            inputs = dict()
            for before in self.predecessors.get(process):
                for output_identifier, value in outputs[before].iteritems():
                    match = self.match[process][before]
                    input_identifier = match[output_identifier] if output_identifier in match else output_identifier
                    inputs[input_identifier] = value
        return inputs

    def _load_outputs(self, results, outputs):
        for result in results:
            outputs[result['process']] = result['outputs']
