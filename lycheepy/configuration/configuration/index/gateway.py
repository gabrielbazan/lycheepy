import redis


class IndexGateway(object):

    def __init__(self, host, port, db):
        self.connection = redis.StrictRedis(host=host, port=port, db=db)

    def publish(self, identifier, metadata):
        return self.connection.set(identifier, metadata)

    def remove(self, identifier):
        return self.connection.delete(identifier)

    def all(self):
        return {
            identifier: self.connection.get(identifier)
            for identifier in self.connection.keys()
        }
