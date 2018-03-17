from pywps import LiteralInput, ComplexInput, LiteralOutput, ComplexOutput, FORMATS, Format
from executable_adapter import ExecutableAdapter


class MetadataBuilder(object):

    def __init__(self, metadata):
        self.metadata = metadata


class ExecutableAdapterBuilder(MetadataBuilder):

    def build(self):
        return ExecutableAdapter(
            [
                ExecutableAdapterInputBuilder(input_metadata).build()
                for input_metadata in self.metadata.get('inputs')
            ],
            [
                ExecutableAdapterOutputBuilder(input_metadata).build()
                for input_metadata in self.metadata.get('outputs')
            ],
            self.metadata.get('identifier'),
            self.metadata.get('version'),
            self.metadata.get('title'),
            self.metadata.get('abstract'),
            self.metadata,
            is_chain='steps' in self.metadata
        )


class ExecutableAdapterParameterBuilder(MetadataBuilder):
    literal = None
    complex = None

    def build(self):
        identifier = self.metadata.get('identifier')
        title = self.metadata.get('title')
        if self.metadata.get('format'):
            parameter_format = getattr(FORMATS, self.metadata.get('format'))
            parameter = self.complex(identifier, title, [Format(parameter_format.mime_type)])
        else:
            parameter = self.literal(identifier, title, data_type=self.metadata.get('dataType'))
        return parameter


class ExecutableAdapterInputBuilder(ExecutableAdapterParameterBuilder):
    literal = LiteralInput
    complex = ComplexInput


class ExecutableAdapterOutputBuilder(ExecutableAdapterParameterBuilder):
    literal = LiteralOutput
    complex = ComplexOutput
