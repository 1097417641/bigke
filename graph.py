from py2neo import Graph, Node, Relationship,NodeMatcher
import LevenshteinDistance
import time
from py2neo.matching import RelationshipMatcher
from model import *
import requests,json
graph = Graph('http://localhost:7474', auth = ('neo4j', '123456'))

def createPeopleNode(name,property,location):
    data = macthPeopleNode(name)
    sum = 0
    s = 0
    if data:
        for p in data:
            if p[0]:
                if p[0]['property']:
                    s += 1
                    dis = LevenshteinDistance.ld(property,p[0]['property'])
                else:
                    dis = LevenshteinDistance.ld(property, '')
                if p[0]['property']:
                    dist = 1 - dis / (len(property) + len(p[0]['property']))
                elif (len(property) + len('')) == 0:
                    dist = 0
                else:
                    dist = 1 - dis / (len(property) + len(''))
                sum += dist
                if p[0]['location']:
                    s += 1
                    dis = LevenshteinDistance.ld(location,p[0]['location'])
                else:
                    dis = LevenshteinDistance.ld(location, '')
                if p[0]['location']:
                    dist = 1 - dis / (len(location) + len(p[0]['location']))
                elif (len(location) + len('')) == 0:
                    dist = 0
                else:
                    dist = 1 - dis / (len(location) + len(''))
                sum += dist
                if s == 0:
                    return p[0]
                sum = sum/s
                if sum > 0.7:
                    return p[0]
    p = Node("Person", name=name, property = property, location = location)
    graph.create(p)
    return p


def createDanganNode(name,property=False):
    p = macthDanganNode(name)
    if p:
        return p
    p = Node("dangan", name=name, property = property)
    graph.create(p)
    return p

def createRelationship(Node1,Node2):
    r1 = Relationship(Node1,"包含",Node2)
    r2 = Relationship(Node2,"被包含",Node1)
    graph.create(r1)
    graph.create(r2)

def createPeopleRel(Node1,Node2):
    r1 = Relationship(Node1,"档案相关",Node2)
    graph.create(r1)



def macthPeopleNode(name):
    mather = NodeMatcher(graph)
    result = graph.run("MATCH (n:Person) where n.name = " + "'" + name + "'" + " RETURN n ")
    return result

def macthDanganNode(name):
    mather = NodeMatcher(graph)
    result = mather.match("dangan", name = name ).first()
    return result



if __name__ == "__main__":
    filepath = "./Docs"
    output = NERmodel(filepath)
    # print(output[0]['people'])


    #print(output)
    # node1 = createPeopleNode('测试','')
    # print(node1['property'])
    # print(node1)


    #lhz 实体对齐测试
    graph.delete_all()
    output = NERmodel("./Docs")
    for triple in output[0]:
        node1 = createDanganNode(triple['filename'])
        num = 0
        #####人物档案关系建立######
        for i in triple['people']:
            if triple['people'][i] and triple['location'] :
                print(triple['people'][i][0])
                print(triple['location'])
                node2 = createPeopleNode(i,triple['people'][i][0],triple['location'])
            elif triple['people'][i] :
                node2 = createPeopleNode(i, triple['people'][i][0],'')
            elif triple['location']:
                node2 = createPeopleNode(i, '', triple['location'])
            else:
                node2 = createPeopleNode(i,'','')
            createRelationship(node1, node2)
        #####人物关系建立#######
        for p1 in triple['people']:
            if triple['people'][p1] and triple['location'] :
                node2 = createPeopleNode(p1,triple['people'][p1][0],triple['location'])
            elif triple['people'][p1] :
                node2 = createPeopleNode(p1, triple['people'][p1][0],'')
            elif triple['location']:
                node2 = createPeopleNode(p1, '', triple['location'])
            else:
                node2 = createPeopleNode(p1,'','')
            for p2 in triple['people']:
                if p1 != p2:
                    if triple['people'][p2] and triple['location']:
                        node1 = createPeopleNode(p2, triple['people'][p2][0], triple['location'])
                    elif triple['people'][p2]:
                        node1 = createPeopleNode(p2, triple['people'][p2][0], '')
                    elif triple['location']:
                        node1 = createPeopleNode(p2, '', triple['location'])
                    else:
                        node1 = createPeopleNode(p2, '', '')
                    createPeopleRel(node1,node2)









