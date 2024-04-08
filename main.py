from flask import Flask, render_template, request, jsonify,redirect
from face_feature import FaceFeature
from face_compare import FaceCompare
from werkzeug.utils import secure_filename
import os
import requests
import time
import hashlib
import base64
import pandas as pd
import json

app = Flask(__name__)

# 人脸特征识别上传文件的目录
UPLOAD_FOLDER = r'C:\\Users\\lenovo\\Desktop\\'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print(app.config['UPLOAD_FOLDER'])

# 人脸特征识别允许上传的文件类型
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# 物体识别参数
URL = "http://tupapi.xfyun.cn/v1/currency"
APPID = "104aec75"
API_SECRET="MjQwMWNhNGRiYjI3ZDRmOGE1NDY3NzI5"
API_KEY = "b293f37c200b7a35a908450caaea3a7f"

# 人脸识别参数
URL1 = "http://tupapi.xfyun.cn/v1/currency"
APPID1 = "24b02ea1"  # 应用ID
API_KEY1 = "0e0e46edc168862498c9b6ef141dcd3a"  # 接口密钥

# 人脸对比参数
APPID2 = '4dce1d80'
API_SECRET2 = 'N2U4MDIzZjFlNWJiY2VmNjlkYmE0MDNh'
API_KEY2 = '0be40011df1ef484e7406bb28afc380f'



#物体识别页面的函数

app = Flask(__name__)

def get_header(image_name):
    cur_time = str(int(time.time()))
    param = "{\"image_name\":\"" + image_name +  "\"}"
    param_base64 = base64.b64encode(param.encode('utf-8'))
    tmp = str(param_base64, 'utf-8')

    m2 = hashlib.md5()
    m2.update((API_KEY + cur_time + tmp).encode('utf-8'))
    check_sum = m2.hexdigest()

    header = {
        'X-CurTime': cur_time,
        'X-Param': param_base64,
        'X-Appid': APPID,
        'X-CheckSum': check_sum,
    }
    return header

def replace_labels_with_chinese(labels):
    df = pd.read_excel("label.xlsx")
    label_map = dict(zip(df['label值'], df['中文']))
    return [label_map[label] if label in label_map else label for label in labels]


def get_body(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

#人脸特征识别界面函数

'''辅助函数：检查文件扩展名是否允许'''
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#人脸对比别界面函数



@app.route('/')
def index():
    return render_template('object_detection.html')  # 设置默认页面为物体识别页面

@app.route('/object_detection')
def object_detection():
    return render_template('object_detection.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file:
        file.save(file.filename)
        file_path = file.filename
        header = get_header(file.filename)
        body = get_body(file_path)
        response = requests.post(URL, headers=header, data=body)
        response_json = response.json()  # Convert response to JSON
        labels = response_json['data']['fileList'][0]["labels"]
        chinese_labels = replace_labels_with_chinese(labels)
        response_json['data']['fileList'][0]["labels"] = chinese_labels
        print(response_json['data']['fileList'][0]["labels"])

        return jsonify({"response": json.dumps(response_json)})


@app.route('/face_recognition')
def face_recognition():
    return render_template('face_recognition.html')


@app.route('/upload1', methods=['POST'])
def upload_file1():
    if 'file1' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file1']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file and allowed_file(file.filename):
        # 保存文件到上传文件夹
        filename = secure_filename(file.filename)
        print(filename)
        filepath = os.path.join(r'C:\\Users\\lenovo\\Desktop\\', filename)
        print(filepath)
        # 进行人脸特征识别
        face_feature = FaceFeature(APPID, API_KEY, filepath)

        result = face_feature.face_local_analysis()
        print(result)
        return jsonify({"response": result})


@app.route('/face_compare')
def face_compare():
    return render_template('face_compare.html')


@app.route('/upload2', methods=['POST'])
def upload_file2():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "No file part"})
    file1 = request.files['file1']
    file2 = request.files['file2']
    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "No selected file"})
    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        # 保存文件到上传文件夹
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        filepath1 = os.path.join(r'C:\\Users\\lenovo\\Desktop\\', filename1)
        filepath2 = os.path.join(r'C:\\Users\\lenovo\\Desktop\\', filename2)
        file1.save(filepath1)
        file2.save(filepath2)
        print()
        # 进行人脸对比
        face_compare = FaceCompare(APPID2, API_SECRET2,API_KEY2, filepath1, filepath2)
        result = face_compare.run()
        print(result)
        return jsonify({"response": result})



if __name__ == '__main__':
    app.run(debug=True)