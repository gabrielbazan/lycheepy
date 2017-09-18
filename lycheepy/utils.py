import pkgutil
import inspect
import sys
import importlib


def get_instances_from_package(package, sub_type_of):
    instances = []
    prefix = package.__name__ + '.'

    for importer, modname, is_pkg in pkgutil.iter_modules(package.__path__, prefix):

        if is_pkg:
            instances.extend(get_instances_from_package(modname, sub_type_of))
        else:
            importlib.import_module(modname)
            class_members = inspect.getmembers(sys.modules[modname], inspect.isclass)

            module_instances = [
                _class()
                for name, _class in class_members
                if issubclass(_class, sub_type_of) and _class is not sub_type_of
            ]

            instances.extend(module_instances)

    return instances
