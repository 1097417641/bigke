from datautils import *
from fastHan import FastHan
import re
import json


def NERmodel(filepath):
    """
    :param filepath: 文件夹路径
    :return:
    """
    model = FastHan()
    filenames, text = extractFile(filepath)  # 需要根据前端多提供的接口改

    # print("{} : {}".format(filenames, text))
    output = []
    triplesList = []
    for i, filename in enumerate(filenames):
        docNum = docsInfo(text[i])
        docDate = docsDate(text[i])
        fileDic = {}
        sentences = cutSentences(text[i])  # 文档切分成句子
        per2org = []
        location = []

        loc_filename = model(filename, target="NER")[0]  # 从档案名称中抽取与地点相关的信息
        for k in range(len(loc_filename)):
            if loc_filename[k][1] == "NS":
                # print(loc_filename[k][0])
                location.append(loc_filename[k][0])

        for item in range(1, len(sentences)):
            tmp = model(sentences[item], target="NER")  # 文章切分句子后，一句话的识别结果
            tmpDic, location = resultProcess(tmp[0], location)
            # print(tmpDic)
            if tmpDic and item > 0:
                triplesList += triplesResult(sentences[item], tmpDic)
            per2org += tmpDic  # 文档内容每句话中的人物与机构对应起来

        per2org = removeSameDic(per2org)
        docLoc = docsLocate(location)
        fileDic["filename"] = filename
        fileDic["docNum"] = docNum
        fileDic["location"] = docLoc
        fileDic["docDate"] = docDate
        fileDic["people"] = per2org
        # print(fileDic)
        output.append(fileDic)

    return output, triplesList


def triplesResult(sentence, per2org):
    """
    :param sentence: 按照文档内容进行切分的句子
    :param per2org: {'per1': [org1, org2]}
    :return:<sen, per, org>
    """
    triplesDict = []
    per, orgs = per2org[0].items()  # per2org的格式固定
    per = per[1]
    orgs = orgs[1]
    if len(orgs) != 0:
        for i in range(len(orgs)):
            tmp_1 = dict()
            tmp_1["sentence"] = sentence
            tmp_1["head"] = per
            tmp_1["head_type"] = 'person'
            tmp_1["tail"] = orgs[i]
            tmp_1["tail_type"] = 'organization'
            triplesDict.append(tmp_1)
            tmp_2 = dict()
            tmp_2["sentence"] = sentence
            tmp_2["head"] = orgs[i]
            tmp_2["head_type"] = 'organization'
            tmp_2["tail"] = per
            tmp_2["tail_type"] = 'person'
            triplesDict.append(tmp_2)

    # print(triplesDict)
    return triplesDict


def docsInfo(text):
    """
    从文档名和文档内容中提取文号
    """
    regular = re.findall(r"\n(.+?)〔(\d+)〕(.+?)号", text)
    # print('regular', regular)

    if regular != [] and len(regular[0]) == 3:  # 提取到的是标准文号
        docNum = regular[0][0] + '〔' + regular[0][1] + '〕' + regular[0][2] + '号'
    else:
        docNum = ''
    # print(docNum)
    return docNum


def docsDate(text):
    """
    从文档中提取日期信息
    """
    text = text.replace(' ', '')  # 去除掉text中的空白符
    # regular = re.findall(r"(\d.+?)年(.+?)月(.+?)日", text)
    regular = re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)

    if regular != [] and len(regular) > 0:
        i = 0
        while len(regular[i]) != 3:  # 找到合法的日期
            i += 1
        docDate = regular[i][0] + '年' + regular[i][1] + '月' + regular[i][2] + '日'
    else:
        docDate = ''
    # print(docDate)
    return docDate


def resultProcess(senList, location):
    """
    将提取结果处理成{'name': 张三, 'organization': ['xx公司']}
    提取关键信息
    """
    person = []
    organization = []
    dic = {}
    dicList = []
    for i in range(len(senList)):
        if senList[i]:
            if senList[i][1] == 'NR':
                person.append(senList[i][0])
                # print(person)
            elif senList[i][1] == 'NT':
                organization.append(senList[i][0])
                # print(organization)
            elif senList[i][1] == 'NS':
                location.append(senList[i][0])
            else:
                continue

    for j in range(len(person)):
        # dic.setdefault(key, []).append(value)
        dic['preson'] = person[j]
        dic['organization'] = []  # 如果没有，该项先为空
        for k in range(len(organization)):
            dic.setdefault('organization', []).append(organization[k])
        dicList.append(dic)
    return dicList, location


def removeSameDic(dicList):
    """
    合并字典中key相同的value（列表）
    """
    handler = {}
    for item in dicList:
        if item["preson"] in handler:
            for i in item["organization"]:
                handler[item["preson"]].append(i)
        else:
            handler[item["preson"]] = item["organization"]  # 用列表方式接收
    return handler


def docsLocate(location):
    """
    利用抽取结果构造地点本体
    且按照与字典匹配到的第一个地点返回
    """
    f2 = open('info.json', 'r', encoding='utf-8')  # JSON到字典转化
    area = json.load(f2)
    special_area = ["香港", "澳门"]  # 特别行政区

    for i in range(len(location)):
        if '市' in location[i]:
            tmpLoc = location[i].replace('市', '')
        else:
            tmpLoc = location[i]
        for key in area:
            if tmpLoc in area[key]:
                province = key
                # print(province)
                if tmpLoc == province:
                    if tmpLoc in special_area:
                        return tmpLoc + "特别行政区"
                    else:
                        return tmpLoc + "市"
                else:
                    return province + "省" + tmpLoc + "市"
