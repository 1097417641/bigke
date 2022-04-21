from flask import Flask,request,jsonify
from query import query_fuzzy, query_exact
from os import path, mkdir
from utils.util import search_logging
from utils.logging import config

app = Flask(__name__)
pwd = "E:\\BIGKE"
BASE_URL = "http://127.0.0.1:8080/document/"
#定义文件的保存路径和文件名尾缀
UPLOAD_FOLDER = path.join(pwd,'save_file')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/search/document', methods=['GET','POST'])
def searchDocumnet():
    #提取request参数
    searchType = request.args.get('searchType')
    searchContent = request.args.get('searchContent')
    matchDegree = request.args.get('matchDegree')
    chronological = request.args.get('chronological')
    start_time = request.args.get('startTime')
    endTime = request.args.get('endTime')
    #请求源的IP地址
    ip = request.remote_addr

    result = {'documents': [], 'nodes':[], "links": {},"categories":[], "code": 0, "personDetail":{}}
    if matchDegree == '0':
        result = query_fuzzy(searchContent, searchType)
    elif matchDegree == '1':
        result = query_exact(searchContent, searchType)

    app.logger.info(search_logging(ip, searchContent, searchType, result))

    if len(result['documents']) != 0:
        json_result = {"data": result, "status":200}
    else:
        json_result = {"data": result, "status": 201}
    #print(json_result)
    return json_result



def allowed_file(filename):
    '''
    检验文件名后缀是否满足格式要求
    :param filename:
    :return:
    '''
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/search/document/upload', methods=['GET', 'POST'])



def uploadPDF():
    '''
    上传文件到save_file文件夹
    with (open('路径','rb') as file_obj:
        rsp = request.post('http://localhost:5000/search/document/upload, file={'file': file_obj}')
        print(rsp.text
    :return:
    '''
    if( 'file' not in request.files):
        return {"status":404, "url": "", "message": "No file part"}
    file = request.files['file']
    if file.filename == "":
        return {"status":404, "url": "", "message": "No file selected"}
    if file and allowed_file(file.filename):
        date = datetime.datetime.now()
        file_name =  str(date.__hash__())    + '.'+file.filename.rsplit('.',1)[1].lower()
        date_str = date.strftime("%Y-%m-%d")
        file_path = path.join(app.config['UPLOAD_FOLDER'], date_str)
        print(file_path)
        if(not path.exists(file_path)):
            mkdir(file_path)
        file.save(path.join(file_path, file_name))
        url = BASE_URL + date_str + "/" + file_name
        return  {"status":200, "url": url, "message": "file upload successfuly"}
    return {"status":404, "url": "", "message": "file upload failed"}


if __name__ == '__main__':
    app.config.from_object(config['development'])
    config['development'].init_app(app)
    app.run()
