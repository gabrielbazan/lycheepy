import sys
import inspect
import pkgutil
import importlib


class DefaultDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def get_instances_from_package(package_name, sub_type_of):
    package = importlib.import_module(package_name)
    path = package.__path__
    prefix = package.__name__ + '.'

    instances = []
    for importer, module_name, is_pkg in pkgutil.iter_modules(path, prefix):
        if is_pkg:
            instances.extend(get_instances_from_package(module_name, sub_type_of))
        else:
            importlib.import_module(module_name)
            module_instances = [
                _class()
                for name, _class in inspect.getmembers(sys.modules[module_name], inspect.isclass)
                if issubclass(_class, sub_type_of) and _class is not sub_type_of
            ]
            instances.extend(module_instances)

    return instances
