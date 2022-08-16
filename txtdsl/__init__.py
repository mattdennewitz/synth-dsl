import collections
import pathlib
from typing import List, Type, Dict, Optional
from pydantic import *
import graphviz
from jinja2 import Template
from slugify import slugify

from .grammar import grammar


ConnectionT = Type["Connection"]
SocketT = Type["Socket"]
ValueT = Type["Value"]


def hash_value(value: str):
    return slugify(value)


class Module(BaseModel):
    name: str
    inputs: Dict[str, List[SocketT]] = []
    outputs: Dict[str, List[SocketT]] = []
    # values: List[ValueT] = []
    values: Dict[str, List] = collections.defaultdict(list)

    def get_key(self):
        return hash_value(self.name)


class Socket(BaseModel):
    name: str  # e.g., "Phase"
    label: Optional[str]

    def display_text(self):
        return self.label or self.name

    def get_key(self):
        return slugify(self.name)


class Value(BaseModel):
    attr: str
    label: Optional[str]
    value: str

    def display_text(self):
        return self.label or self.attr


class Connection(BaseModel):
    sender_module: Module
    sender_socket: Socket
    receiver_module: Socket
    receiver_socket: Socket

    def get_edge(self):
        return [self.get_left_edge(), self.get_right_edge()]

    def get_left_edge(self):
        return f"{self.sender_module.get_key()}:{self.sender_socket.get_key()}"

    def get_right_edge(self):
        return f"{self.receiver_module.get_key()}:{self.receiver_socket.get_key()}"


class Patch(BaseModel):
    modules: Dict[str, Module] = {}
    connections: List[ConnectionT] = []

    def get_or_create_module(self, name: str) -> Module:
        if name not in self.modules:
            self.modules[name] = Module(name=name)

        return self.modules[name]

    def get_edges(self):
        return [connection.get_edge() for connection in self.connections]


def parse_patch(schematic: str) -> Patch:
    """Parses a patch schematic into a usable graph"""

    parsed: list = grammar.parseString(schematic, parseAll=True)
    patch = Patch()

    print(parsed)

    for name, configs in parsed:
        module = patch.get_or_create_module(name)

        for line in configs:
            try:
                attr, op, value, label = line
            except ValueError:
                attr, op, value = line
                label = None

            if op == ">":
                for destination in value:
                    d_bits = destination.split(".")
                    if len(d_bits) == 2:
                        dst_module_name, dst_attr = d_bits
                        dst_module = patch.get_or_create_module(dst_module_name)

                        sender_socket = Socket(name=attr, label=label)
                        receiver_socket = Socket(name=dst_attr, label=label)

                        connection = Connection(
                            sender_module=module,
                            sender_socket=sender_socket,
                            receiver_module=dst_module,
                            receiver_socket=receiver_socket,
                        )

                        if sender_socket not in module.outputs:
                            module.outputs.append(sender_socket)

                        if receiver_socket not in dst_module.inputs:
                            dst_module.inputs.append(receiver_socket)

                        if not connection in patch.connections:
                            patch.connections.append(connection)
            elif op == ":":
                # module.values.append(Value(attr=attr, label=label, value=value))
                if "." in attr:
                    header, remainder = attr.split(".", 1)
                    module.values[header].append(
                        Value(attr=remainder, label=label, value=value)
                    )
                else:
                    module.values["default"].append(
                        Value(attr=attr, label=label, value=value)
                    )

    return patch


def render_patch(patch: Patch):
    """Converts a parsed schematic graph into a Graphiz display"""

    template_path = pathlib.Path(__file__).parent.joinpath("./table.j2")
    html = open(template_path).read()
    template = Template(html)

    graph = graphviz.Digraph("structs", node_attr={"shape": "plaintext"})
    edges = []

    for module_name, module in patch.modules.items():
        rendered = template.render(module=module)
        graph.node(module.get_key(), f"<{rendered}>")

    graph.edges(patch.get_edges())

    graph.view()
