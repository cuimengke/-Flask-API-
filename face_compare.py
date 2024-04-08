#
# 人脸比对 WebAPI 接口调用示例
# 运行前：请先填写Appid、APIKey、APISecret以及图片路径
# 运行方法：直接运行 main 即可 
# 结果： 控制台输出结果信息
# 
# 接口文档（必看）：https://www.xfyun.cn/doc/face/xffaceComparisonRecg/API.html
#

from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


class FaceCompare:

    def __init__(self, appid, api_secret, api_key, path1, path2, server_id='s67c9c78c'):
        # 请填写控制台获取的APPID、APISecret、APIKey以及要比对的图片路径
        self.appid = appid
        self.api_secret = api_secret
        self.api_key = api_key
        self.server_id = server_id
        self.base_url = 'http://api.xf-yun.com/v1/private/{}'
        self.img1_path = path1
        self.img2_path = path2

    def __parse_url(self, requset_url):
        """
        url
        :param requset_url:
        :return:
        """
        stidx = requset_url.index("://")
        host = requset_url[stidx + 3:]
        schema = requset_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise AssembleHeaderException("invalid request url:" + requset_url)
        path = host[edidx:]
        host = host[:edidx]
        u = Url(host, path, schema)
        return u

    def __assemble_ws_auth_url(self, requset_url, method="GET"):
        u = self.__parse_url(requset_url)
        host = u.host
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        print(date)
        # date = "Thu, 12 Dec 2019 01:57:27 GMT"
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        print(signature_origin)
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        print(authorization_origin)
        values = {"host": host, "date": date, "authorization": authorization}
        return requset_url + "?" + urlencode(values)

    def __gen_body(self):
        """
        请求参数配置
        :return:
        """
        with open(self.img1_path, 'rb') as f:
            img1_data = f.read()
        with open(self.img2_path, 'rb') as f:
            img2_data = f.read()
        body = {"header": {"app_id": self.appid, "status": 3}, "parameter": {
            self.server_id: {"service_kind": "face_compare",
                             "face_compare_result": {"encoding": "utf8", "compress": "raw", "format": "json"}}},
                "payload": {
                    "input1": {"encoding": "jpg", "status": 3, "image": str(base64.b64encode(img1_data), 'utf-8')},
                    "input2": {"encoding": "jpg", "status": 3, "image": str(base64.b64encode(img2_data), 'utf-8')}}}
        return json.dumps(body)

    def get_data(self):
        """
        1.构造请求url、头域等信息
        2.向服务器发送请求
        3.接收服务器端的返回结果
        :return: 响应数据
        """
        # 获取人脸比对接口
        url = self.base_url.format(self.server_id)
        request_url = self.__assemble_ws_auth_url(url, "POST")
        headers = {'content-type': "application/json",
                   'host': 'api.xf-yun.com', 'app_id': self.appid}
        response = requests.post(request_url, data=self.__gen_body(), headers=headers)
        resp_data = json.loads(response.content.decode('utf-8'))
        return resp_data

    def process_data(self, resp_data):
        """
        结果处理
        :param resp_data: 原始数据
        :return:
        """
        # 对获取的json换进行处理
        compare_result = {}
        code = resp_data['header']['code']
        if code > 0:
            compare_result['score'] = '0'
            compare_result['desc'] = str(code) + resp_data['header']['message']
        else:
            result = base64.b64decode(resp_data['payload']['face_compare_result']['text']).decode()
            score = float(json.loads(result)['score'])
            compare_result['score'] = "%.2f%%" % (score * 100)
            if score < 0.67:
                compare_result['desc'] = '同一个人可能性极低'
            else:
                compare_result['desc'] = '可能是同一人'
        return compare_result

    def run(self):
        """
        人脸比对识别
        :return:
        """
        # 调用get_data方法获取从服务器请求的数据
        resp_data = self.get_data()
        # 调用process_data方法将数据进行解析
        compare_result = self.process_data(resp_data)
        return compare_result


# 请填写控制台获取的APPID、APISecret、APIKey以及要比对的图片路径
if __name__ == '__main__':
    img1_path = r'C:\\Users\\lenovo\\Desktop\\hemin2.jpg'
    img2_path = r'C:\\Users\\lenovo\\Desktop\\hemin1.jpg'
    appid = '4dce1d80'
    api_secret = 'N2U4MDIzZjFlNWJiY2VmNjlkYmE0MDNh'
    api_key = '0be40011df1ef484e7406bb28afc380f'
    res = FaceCompare(appid, api_secret, api_key, img1_path, img2_path).run()
    print(res)
