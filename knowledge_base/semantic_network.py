class SemanticNetwork:
    def __init__(self, destinations, activities):
        self.graph = {}
        by_name = {a["name"]: a for a in activities}
        for destination in destinations:
            name = destination["name"]
            self.add(name, "IS-A", destination["type"])
            for interest in destination["interests"]:
                self.add(name, "HAS-INTEREST", interest)
            for transport in destination["transport"]:
                self.add(name, "SUPPORTS", transport)
            for accommodation in destination["accommodation"]:
                self.add(name, "HAS-ACCOMMODATION", accommodation)
            for activity_name in destination["activities"]:
                self.add(name, "OFFERS", activity_name)
                activity = by_name.get(activity_name)
                if activity:
                    for tag in activity["tags"]:
                        self.add(activity_name, "TAGGED-AS", tag)

    def add(self, source, relation, target):
        self.graph.setdefault(source, []).append({"relation": relation, "target": target})

    def neighbors(self, node):
        return [edge["target"] for edge in self.graph.get(node, [])]

    def facts(self):
        return self.graph
