from py2neo import NodeMatcher,RelationshipMatcher
from graph import graph
from best_node import b1st_node

node_matcher = NodeMatcher(graph)
relationship_matcher = RelationshipMatcher(graph)
#
#节点类别映射表：从中文 -> 英文
categoryToCHN = {"dangan":"档案", "Person":"人物"}

#
def query(keyword, method, search=['false','false']):
    data = []
    if method == 'true':
        if search[0] == 'true':
            nodes = node_matcher.match('Person').where("_.name =~ '.*%s.*'" % keyword)
            best_data, data = b1st_node(keyword, nodes)
        elif search[1] == 'true':
            nodes = node_matcher.match('dangan').where("_.name =~ '.*%s.*'" % keyword)
            best_data, data = b1st_node(keyword, nodes)
        else:
            nodes = node_matcher.match().where(
                "_.name =~ '.*%s.*'" % keyword)
            best_data, data = b1st_node(keyword, nodes)
        data = list(data)
        best_data = list(best_data)
        print(best_data)
    elif method == 'false':
        if search[0] == 'true':
            nodes = node_matcher.match('Person').where("_.name =~ '%s'" % keyword)
            for node in nodes:
                data += list(relationship_matcher.match([node], r_type=None))
        elif search[1] == 'true':
            nodes = node_matcher.match('dangan').where("_.name =~ '%s'" % keyword)
            for node in nodes:
                data += list(relationship_matcher.match([node], r_type=None))
        else:
            nodes = node_matcher.match().where("_.dangan =~ '%s'  or _.name =~ '%s'" % (keyword, keyword))
            for node in nodes:
                data += list(relationship_matcher.match([node], r_type=None))
        data = list(data)
    #checkout_data(data[0])
    #return get_json_data(data)



'''
模糊检索
'''
def query_fuzzy(keyword, type):
    data = []
    if type == 'person':
        nodes = node_matcher.match('Person').where("_.name =~ '.*%s.*'" % keyword)
        best_data, data = b1st_node(keyword, nodes)
    elif type == 'document':
        nodes = node_matcher.match('dangan').where("_.name =~ '.*%s.*'" % keyword)
        best_data, data = b1st_node(keyword, nodes)
    else:
        nodes = node_matcher.match().where(" _.name =~ '.*%s.*'" % ( keyword))
        best_data, data = b1st_node(keyword, nodes)
    data = list(data)
    best_data = list(best_data)
    #print(data)
    return get_json_data(data, type)


def query_exact(keyword, type):
    data = []
    if type == 'penson':
        nodes = node_matcher.match('Person').where("_.name =~ '%s'" % keyword)
        for node in nodes:
            data += list(relationship_matcher.match([node], r_type=None))
    elif type == 'document':
        nodes = node_matcher.match('dangan').where("_.name =~ '%s'" % keyword)
        for node in nodes:
            data += list(relationship_matcher.match([node], r_type=None))
    else:
        nodes = node_matcher.match().where("_.dangan =~ '%s'  or _.name =~ '%s'" % (keyword, keyword))
        for node in nodes:
            data += list(relationship_matcher.match([node], r_type=None))
    data = list(data)
    print(data)
    return get_json_data(data, type)



def get_json_data(data, searchType):
    json_data = {'documents': [], 'nodes':[], "links": {},"personDetail":{},"categories":[], "code": 0}
    d = []
    for i in data:
        #print(i)
        if list(i.start_node.labels)[0] == "dangan":
            start_node_str = i.start_node['name'] + "_" + str(i.start_node.identity) +"_" + list(i.start_node.labels)[0]
            end_node_str = i.end_node['name'] + "_" + str(i.end_node.identity) + "_" + list(i.end_node.labels)[0]
        else:
            start_node_str = i.start_node['name'] + "_" + str(i.start_node.identity) + "_" + list(i.start_node.labels)[0]
            end_node_str = i.end_node['name'] + "_" + str(i.end_node.identity) + "_" + list(i.end_node.labels)[
                0]
        d.append(start_node_str)
        d.append(end_node_str)

    d1 = list(set(d))
    d1.sort(key = d.index)
    #print(d1)
    name_dict = {}
    category_set= set()
    #count = 0
    for j in d1:
        j_array = j.split("_")
        data_item = {}
        category_set.add(j_array[2])
        name_dict[j_array[0]] = j_array[1]
       # count += 1
        data_item['name'] = j_array[0]
        data_item['id'] = j_array[1]
        data_item['category'] = categoryToCHN[j_array[2]]
        # j_array[1] = j_array[1].strip()
        # data_item['category'] = CA_LIST[j_array[1]]
        json_data['nodes'].append(data_item)
        if j_array[2] == "dangan":
            json_data['documents'].append(data_item)


    for category in list(category_set):
        json_data['categories'].append({'name': categoryToCHN[category]})


    for document in json_data['documents']:
        json_data['links'][document['id']] = []

    for node in json_data['nodes']:
        if node['category'] == "人物":
            json_data['personDetail'][node['id']] = []


    '''
        if searchType == "person":
        for i in data:
            link_item = {}
            documnet_id = str(i.end_node.identity)
            person_id = str(i.start_node.identity)
            if documnet_id in json_data['links'].keys():
                link_item['source'] = str(i.start_node.identity)
                link_item['target'] = documnet_id
                link_item['name'] = type(i).__name__
                json_data['links'][documnet_id].append(link_item)

            if person_id in json_data['personDetail'].keys():
                json_data['personDetail'][person_id].append((str(i)))


    else:
    
    '''

    for i in data:
        link_item = {}
        if(type(i).__name__ == '包含'):

            documnet_id = str(i.start_node.identity)
            person_id = str(i.end_node.identity)
            if documnet_id in json_data['links'].keys():
                link_item['source'] = documnet_id
                link_item['target'] = name_dict[i.end_node['name']]
                link_item['name'] = type(i).__name__
                json_data['links'][documnet_id].append(link_item)

            if person_id in json_data['personDetail'].keys():
                json_data['personDetail'][person_id].append((str(i)))
        elif (type(i).__name__ == "被包含"):
            documnet_id = str(i.end_node.identity)
            person_id = str(i.start_node.identity)
            if documnet_id in json_data['links'].keys():
                link_item['source'] = str(i.start_node.identity)
                link_item['target'] = documnet_id
                link_item['name'] = type(i).__name__
                json_data['links'][documnet_id].append(link_item)

            if person_id in json_data['personDetail'].keys():
                json_data['personDetail'][person_id].append((str(i)))



    #print(json_data)
    return json_data



#query_fuzzy('吴锦忠',"all" )
#query('张飞', method='true')