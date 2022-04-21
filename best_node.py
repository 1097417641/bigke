from py2neo import NodeMatcher,RelationshipMatcher,Node
from graph import graph
from thefuzz import fuzz
import pandas

node_matcher = NodeMatcher(graph)
relationship_matcher = RelationshipMatcher(graph)


def b1st_node(keyword,nodes):
    data = []
    score = 0
    best_node = graph.create(Node())
    for node in nodes:
        if fuzz.ratio(keyword, node['name']) > score:
            score = fuzz.ratio(keyword, node['name'])
            if list(node.labels)[0] == 'dangan':
                best_node = node
            else:
                str_name = node['name']
                cypher = "MATCH {} - [: 被包含]-(m) RETURN m".format(node)
                print(cypher)
                best_node = graph.run(cypher).data()[0]['m']
            #best_node = node
        data += list(relationship_matcher.match([node], r_type=None))
    best_data = list(relationship_matcher.match([best_node], r_type=None))
    return best_data,data