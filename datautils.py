import pdfplumber
import os
import re
import json


def extractFile(path):
    """
    根据文件类型选择不同的读取方式
    """
    files = os.listdir(path)
    filenames = []
    text = []
    for file in files:
        if not os.path.isdir(file):
            # print(file)
            suffix = file.split('.')[1]
            # print(suffix)
            if suffix == "pdf":
                filename, content = readPDF(path + '/' + file)
            elif suffix == "txt":
                filename, content = readTXT(path + '/' + file)
            filenames.append(filename)
            text.append(content)
    return filenames, text


def readPDF(filepath):
    """
    从PDF中提取文档名、文档内容
    """
    filename = os.path.basename(filepath)  # 带后缀的文件名
    filename = filename.split('.')[0]  # 不带后缀的文件名
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
        return filename, text


def readTXT(filepath):
    """
    读取txt文件内容
    """
    filename = os.path.basename(filepath)  # 带后缀的文件名
    filename = filename.split('.')[0]
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    return filename, text


def removeSpace(text):
    """
    去除文档内容中的空格和换行符
    """
    text = text.replace(' ', '')
    text = text.replace('\n', '')
    return text


def cutSentences(text):
    """
    将文档内容分成若干句子，以分号、冒号、句号作为切分
    """
    text = removeSpace(text)

    start = 0
    result = []
    groups = re.finditer('：|:|;|；|。|', text)
    for i in groups:
        end = i.span()[1]
        result.append(text[start:end])
        start = end
    # last one
    result.append(text[start:])
    # print(result)
    tmp = ''
    sentences = []
    for i in range(len(result) - 1):
        tmp += result[i]
        if result[i] != '' and result[i + 1] == '':
            sentences.append(tmp)
            tmp = ''

    # print(sentences)
    return sentences


def cutLongText(text):
    """
    将长段落字符串分成长度为500的短字符串
    """
    count = int(len(text) / 500)
    # print(count)
    flag = 1
    textPieces = []
    if count == 0:
        flag = 0
        textPieces.append(text)
    else:
        for i in range(count):
            tmp = text[i * 500: (i + 1) * 500 - 1]
            textPieces.append(tmp)
        tmp = text[(i + 1) * 500:]
        textPieces.append(tmp)
    return textPieces, flag


def save2json(filename, result):
    length = len(result)

    with open(filename, "w", encoding="utf-8") as f:
        f.write('[')
        for i in range(length):
            json.dump(result[i], f, ensure_ascii=False)
            if i == length - 1:
                f.write("]")
            else:
                f.write(',')
                f.write('\n')
