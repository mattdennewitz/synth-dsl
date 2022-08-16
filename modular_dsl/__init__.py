import copy


__all__ = ("Input", "Module", "Output")

from collections import defaultdict

from typing import Optional, List

import graphviz
from jinja2 import Template


class Port:
    """Base class for an input or output"""

    def __init__(self, label=None):
        self.label = label

    def _get_bound_field(self, module, name):
        return BoundField(module=module, name=name, label=self.label)


class IO(Port):
    pass


class Value(Port):
    pass


class BoundField:
    def __init__(self, module, name, label):
        self.module = module
        self.name = name
        self.label = label

    def __call__(self, value):
        self.module._data[self] = value
        return self.module

    def __rshift__(self, receiver: IO):
        """Connects an output to an input"""

        self._add_connection(receiver)
        return self

    def _add_connection(self, receiver: IO):
        if not receiver in self.module._connections:
            self.module._connections[self].append(receiver)

    def __str__(self):
        return f"{self.module.__class__.__name__}.{self.name}"

    def value(self):
        return self.module._data.get(self) or ""

    def port_key(self):
        return self.name

    def display_text(self):
        return self.label or self.name


class FieldConnectionMetaclass(type):
    def __new__(cls, name, bases, attrs):
        base_fields = {}

        for (key, field) in list(attrs.items()):
            if not isinstance(field, Port):
                continue

            attrs.pop(key)
            base_fields[key] = field

        new_class = super().__new__(cls, name, bases, attrs)
        new_class.base_fields = base_fields

        return new_class


class BaseModule:
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        self.fields = copy.deepcopy(self.base_fields)
        self._cached_bound_fields = {}
        self._connections = defaultdict(list)
        self._data = {}

    def __getattr__(self, name):
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(f"no field named {name}")

        if name in self._cached_bound_fields:
            return self._cached_bound_fields[name]

        self._cached_bound_fields[name] = field._get_bound_field(self, name)
        return self._cached_bound_fields[name]

    def get_connections(self):
        return self._connections

    def get_configuration(self):
        return self._data

    def get_io_fields(self):
        for key in self.fields:
            if isinstance(self.fields[key], IO):
                yield getattr(self, key)

    def get_value_fields(self):
        for key in self.fields:
            if isinstance(self.fields[key], Value):
                yield getattr(self, key)


class Module(BaseModule, metaclass=FieldConnectionMetaclass):
    def __str__(self):
        return self.name


class Surface:
    def __init__(self):
        self.modules: List[Module] = []

    def __lshift__(self, module):
        if not module in self.modules:
            self.modules.append(module)

        return self

    def render(self):
        template = Template(open("./table.j2").read())
        graph = graphviz.Digraph("structs", node_attr={"shape": "plaintext"})
        edges = []

        for module in self.modules:
            rendered = template.render(module=module)
            graph.node(module.name, f"<{rendered}>")

            # wire connections
            for field, destinations in module.get_connections().items():
                for destination in destinations:
                    edges.append(
                        [
                            f"{module.name}:{field.port_key()}",
                            f"{destination.module.name}:{destination.port_key()}",
                        ]
                    )

        graph.edges(edges)

        graph.view()
