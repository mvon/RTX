import yaml
import os


class Metagraph:
    node_types, relationship_types = {}, {}

    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "metagraph.yaml"), 'r') as stream:
            try:
                data = yaml.load(stream)
                self.node_types = data['node_types']
                self.relationship_types = data['relationship_types']
            except yaml.YAMLError as exc:
                print(exc)

    #   node types
    def get_nodes_name(self, node_type):
        if node_type in self.node_types.keys():
            return self.node_types[node_type]['name']
        else:
            return None

    def get_nodes_curie_prefix(self, node_type):
        if node_type in self.node_types.keys():
            return self.node_types[node_type]['curie_prefix']
        else:
            return None

    def get_nodes_GO_molec_predicate(self, node_type):
        if node_type in self.node_types.keys():
            if 'GO_molec_predicate' in self.node_types[node_type]:
                return self.node_types[node_type]['GO_molec_predicate']
        return None

    #   relationship types
    def get_relation_name(self, relation_type):
        if relation_type in self.relationship_types.keys():
            return self.relationship_types[relation_type]['name']
        else:
            return None

    def get_relation_is_directed(self, relation_type):
        if relation_type in self.relationship_types.keys():
            return self.relationship_types[relation_type]['is_directed']
        else:
            return None

    def get_relation_edge(self, relation_type):
        nodes = self.relationship_types[relation_type]['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.get_relation_name(relation_type), data['target']])
        return relations


if __name__ == '__main__':
    mg = Metagraph()

    #   node types
    print(mg.get_nodes_name('anatomical_entity'))
    print(mg.get_nodes_curie_prefix('anatomical_entity'))
    print(mg.get_nodes_GO_molec_predicate('anatomical_entity'))

    print(mg.get_nodes_name('biological_process'))
    print(mg.get_nodes_curie_prefix('biological_process'))
    print(mg.get_nodes_GO_molec_predicate('biological_process'))

    #   relationship type
    print(mg.get_relation_name('affects'))
    print(mg.get_relation_is_directed('affects'))
    print(mg.get_relation_edge('affects'))

    print(mg.get_relation_name('physically_interacts_with'))
    print(mg.get_relation_is_directed('physically_interacts_with'))
    print(mg.get_relation_edge('physically_interacts_with'))

