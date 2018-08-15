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
    def anatomical_entity(self):
        return self.node_types['anatomical_entity']['name']

    def biological_process(self):
        return self.node_types['biological_process']['name']

    def cellular_component(self):
        return self.node_types['cellular_component']['name']

    def chemical_substance(self):
        return self.node_types['chemical_substance']['name']

    def disease(self):
        return self.node_types['disease']['name']

    def metabolite(self):
        return self.node_types['metabolite']['name']

    def microRNA(self):
        return self.node_types['microRNA']['name']

    def pathway(self):
        return self.node_types['pathway']['name']

    def molecular_function(self):
        return self.node_types['molecular_function']['name']

    def phenotypic_feature(self):
        return self.node_types['phenotypic_feature']['name']

    def protein(self):
        return self.node_types['protein']['name']

    def affects(self):
        return self.relationship_types['affects']['name']

    #   relationship types
    def affects_relations(self):
        nodes = self.relationship_types['affects']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.affects(), data['target']])
        return relations

    def capable_of(self):
        return self.relationship_types['capable_of']['name']

    def capable_of_relations(self):
        nodes = self.relationship_types['capable_of']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.capable_of(), data['target']])
        return relations

    def contraindicated_for(self):
        return self.relationship_types['contraindicated_for']['name']

    def contraindicated_for_relations(self):
        nodes = self.relationship_types['contraindicated_for']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.contraindicated_for(), data['target']])
        return relations

    def expressed_in(self):
        return self.relationship_types['expressed_in']['name']

    def expressed_in_relations(self):
        nodes = self.relationship_types['expressed_in']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.expressed_in(), data['target']])
        return relations

    def gene_associated_with_condition(self):
        return self.relationship_types['gene_associated_with_condition']['name']

    def gene_associated_with_condition_relations(self):
        nodes = self.relationship_types['gene_associated_with_condition']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.gene_associated_with_condition(), data['target']])
        return relations

    def gene_mutations_contribute_to(self):
        return self.relationship_types['gene_mutations_contribute_to']['name']

    def gene_mutations_contribute_to_relations(self):
        nodes = self.relationship_types['gene_mutations_contribute_to']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.gene_mutations_contribute_to(), data['target']])
        return relations

    def has_part(self):
        return self.relationship_types['has_part']['name']

    def has_part_relations(self):
        nodes = self.relationship_types['has_part']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.has_part(), data['target']])
        return relations

    def has_phenotype(self):
        return self.relationship_types['has_phenotype']['name']

    def has_phenotype_relations(self):
        nodes = self.relationship_types['has_phenotype']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.has_phenotype(), data['target']])
        return relations

    def indicated_for(self):
        return self.relationship_types['indicated_for']['name']

    def indicated_for_relations(self):
        nodes = self.relationship_types['indicated_for']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.indicated_for(), data['target']])
        return relations

    def involved_in(self):
        return self.relationship_types['involved_in']['name']

    def involved_in_relations(self):
        nodes = self.relationship_types['involved_in']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.involved_in(), data['target']])
        return relations

    def participates_in(self):
        return self.relationship_types['participates_in']['name']

    def participates_in_relations(self):
        nodes = self.relationship_types['participates_in']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.participates_in(), data['target']])
        return relations

    def physically_interacts_with(self):
        return self.relationship_types['physically_interacts_with']['name']

    def physically_interacts_with_relations(self):
        nodes = self.relationship_types['physically_interacts_with']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.physically_interacts_with(), data['target']])
        return relations

    def regulates(self):
        return self.relationship_types['regulates']['name']

    def regulates_relations(self):
        nodes = self.relationship_types['regulates']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.regulates(), data['target']])
        return relations

    def subclass_of(self):
        return self.relationship_types['subclass_of']['name']

    def subclass_of_relations(self):
        nodes = self.relationship_types['subclass_of']['nodes']
        relations = []
        for data in nodes:
            relations.append([data['source'], self.subclass_of(), data['target']])
        return relations


if __name__ == '__main__':
    mg = Metagraph()
    #   node types
    print(mg.anatomical_entity())
    print(mg.biological_process())
    print(mg.cellular_component())
    print(mg.chemical_substance())
    print(mg.disease())
    print(mg.metabolite())
    print(mg.microRNA())
    print(mg.pathway())
    print(mg.molecular_function())
    print(mg.phenotypic_feature())
    print(mg.protein())

    #   relationship type
    print(mg.affects())
    print(mg.affects_relations())
    print(mg.capable_of())
    print(mg.capable_of_relations())
    print(mg.contraindicated_for())
    print(mg.contraindicated_for_relations())
    print(mg.expressed_in())
    print(mg.expressed_in_relations())
    print(mg.gene_associated_with_condition())
    print(mg.gene_associated_with_condition_relations())
    print(mg.gene_mutations_contribute_to())
    print(mg.gene_mutations_contribute_to_relations())
    print(mg.has_part())
    print(mg.has_part_relations())
    print(mg.has_phenotype())
    print(mg.has_phenotype_relations())
    print(mg.indicated_for())
    print(mg.indicated_for_relations())
    print(mg.involved_in())
    print(mg.involved_in_relations())
    print(mg.participates_in())
    print(mg.participates_in_relations())
    print(mg.physically_interacts_with())
    print(mg.physically_interacts_with_relations())
    print(mg.regulates())
    print(mg.regulates_relations())
    print(mg.subclass_of())
    print(mg.subclass_of_relations())

