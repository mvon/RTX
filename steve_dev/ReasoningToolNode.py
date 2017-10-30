import neo4j.v1

class ReasoningToolNode(neo4j.v1.types.Node):
    def __init__(self):
        pass
    
    def get_biotype(self):
        print(self.labels)
        labels = self.labels.copy()
        print(labels)
        labels.remove("Base")
        print(labels)
        assert len(labels)==1
        return list(labels)[0]

    def get_bioname(self):
        properties = self.properties
        return properties["name"]
    
    def is_expanded(self):
        return self.properties["expanded"] == "true"
    
    def get_uuid(self):
        return self.properties["UUID"]
    