import json
import random

class PyDepGraphSigmaJs(object):

    def get_node(self, label, size):
        id = label
        label = "{}:{}us".format(label, size)
        size = size or 1
        x = "{:.5f}".format(random.uniform(0, 1))
        y = "{:.5f}".format(random.uniform(0, 1))
        return {"id": id, "label": label, "size": size, "x": x, "y": y}
    
    def get_edge(self, a, b):
        id = "{}->{}".format(b.name, a.name)
        return {"id": id, "source": b.name, "target": a.name}

    def get_json_data(self, depgraph):
        nodes = {}
        edges = {}

        for a, b in depgraph:
            # b imports a
            anode = self.get_node(a.name, a.import_time)
            bnode = self.get_node(b.name, b.import_time)
            nodes[anode["id"]] = anode
            nodes[bnode["id"]] = bnode
            edge = self.get_edge(a, b)
            edges[edge["id"]] = edge

        out = {"nodes": list(nodes.values()), "edges": list(edges.values())}
        return out

    def render(self, depgraph):
        data = self.get_json_data(depgraph)
        return json.dumps(data, indent=1)


def dep2sigmajs(depgraph):
    return PyDepGraphSigmaJs().render(depgraph)

