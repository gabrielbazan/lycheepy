

class OutputsDeserializer(object):

    @staticmethod
    def add_data(json, output):
        if json['type'] == 'complex':
            output.file = json['file']
            output.source = json['source']
            output.as_reference = json['as_reference']
        else:
            output.data = json['data']
        return output
