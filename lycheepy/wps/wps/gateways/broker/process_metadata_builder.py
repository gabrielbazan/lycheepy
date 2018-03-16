from pywps import LiteralInput, ComplexInput, LiteralOutput, ComplexOutput, FORMATS, Format
from process_metadata import ProcessMetadata


class MetadataBuilder(object):

    def __init__(self, metadata):
        self.metadata = metadata


class ProcessMetadataBuilder(MetadataBuilder):

    def build(self):
        return ProcessMetadata(
            [
                ProcessMetadataInputBuilder(input_metadata).build()
                for input_metadata in self.metadata.get('inputs')
            ],
            [
                ProcessMetadataOutputBuilder(input_metadata).build()
                for input_metadata in self.metadata.get('outputs')
            ],
            self.metadata.get('identifier'),
            self.metadata.get('version'),
            self.metadata.get('title'),
            self.metadata.get('abstract')
        )


class ProcessMetadataParameterBuilder(MetadataBuilder):
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


class ProcessMetadataInputBuilder(ProcessMetadataParameterBuilder):
    literal = LiteralInput
    complex = ComplexInput


class ProcessMetadataOutputBuilder(ProcessMetadataParameterBuilder):
    literal = LiteralOutput
    complex = ComplexOutput
