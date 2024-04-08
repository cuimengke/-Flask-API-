import requests
import time
import hashlib
import base64
import json


class FaceDesc:
    def __init__(self, label):
        self.label = label

    def convert_age(self):
        age = int(self.label)
        if age == 0:
            result = '0-1'
        elif age == 1:
            result = '2-5'
        elif age == 2:
            result = '6-10'
        elif age == 3:
            result = '11-15'
        elif age == 4:
            result = '16-20'
        elif age == 5:
            result = '21-25'
        elif age == 6:
            result = '31-40'
        elif age == 7:
            result = '41-50'
        elif age == 8:
            result = '51-60'
        elif age == 9:
            result = '61-80'
        elif age == 10:
            result = '80以上'
        elif age == 12:
            result = '26-30'
        elif age == 11:
            result = '其他'
        else:
            result = '图片文件有错误，或者格式不支持（gif图不支持）'
        return result

    def convert_score(self):
        score = int(self.label)
        if score == 0:
            result = '漂亮'
        elif score == 1:
            result = '好看'
        elif score == 2:
            result = '普通'
        elif score == 3:
            result = '难看'
        elif score == 4:
            result = '其他'
        elif score == 5:
            result = '半人脸'
        elif score == 6:
            result = '多人'
        else:
            result = '图片文件有错误，或者格式不支持（gif图不支持）'
        return result

    def convert_sex(self):
        sex = int(self.label)
        if sex == 0:
            result = '男人'
        elif sex == 1:
            result = '女人'
        elif sex == 2:
            result = '难以辨认'
        elif sex == 3:
            result = '多人'
        else:
            result = '图片文件有错误，或者格式不支持（gif图不支持）'
        return result

    def convert_expression(self):
        exp = int(self.label)
        if exp == 0:
            result = '其他(非人脸表情图片)'
        elif exp == 1:
            result = '其他表情'
        elif exp == 2:
            result = '喜悦'
        elif exp == 3:
            result = '愤怒'
        elif exp == 4:
            result = '悲伤'
        elif exp == 5:
            result = '惊恐'
        elif exp == 6:
            result = '厌恶'
        elif exp == 7:
            result = '中性  '
        else:
            result = '图片文件有错误，或者格式不支持（gif图不支持）'
        return result


class FaceFeature:
    def __init__(self, APPID, API_KEY, path):
        """
        构造函数，初始化数据
        :param APPID: 应用ID
        :param API_KEY: # 接口密钥
        :param path: 图片路径
        """
        self.APPID = APPID  # 应用ID
        self.API_KEY = API_KEY  # 接口密钥
        self.base_url = "http://tupapi.xfyun.cn/v1/"  # 基础url
        self.image_path = path  # 图片路径
        self.mode = 0  # 图片路径模式：0- 本地图片；1-网络图片

    def __get_header(self):

        # 根据图片路径模式，构建param
        if self.mode == 0:  # 本地
            param = "{\"image_name\":\"" + self.image_path + "\"}"
        else:  # url
            image_name = 'img.jpg'
            param = "{\"image_name\":\"" + image_name + "\",\"image_url\":\"" + self.image_path + "\"}"
        # 构建头域中的X-Param
        curTime = str(int(time.time()))
        # 构建头域中的X-CheckSum
        paramBase64 = base64.b64encode(param.encode('utf-8'))
        # 构建头域中的X-CheckSum
        tmp = str(paramBase64, 'utf-8')
        m2 = hashlib.md5()
        m2.update((self.API_KEY + curTime + tmp).encode('utf-8'))
        checkSum = m2.hexdigest()
        # 头域
        header = {
            'X-CurTime': curTime,
            'X-Param': paramBase64,
            'X-Appid': self.APPID,
            'X-CheckSum': checkSum,
        }
        return header

    def __get_body(self):
        """
        图片二进制数据
        :return:
        """
        binfile = open(self.image_path, 'rb')
        data = binfile.read()
        return data

    def __get_data_by_type(self, type, headers, data=None):
        """
        1.向服务器端发送请求，接收服务器端的返回结果
        :param type: 类型
        :param data: 图片数据
        :param headers:请求头
        :return:
        """
        try:
            result = requests.post(self.base_url + type, data=data, headers=headers)
            result = json.loads(result.content)
            code = result['code']
            if code == 0:
                label = result['data']['fileList'][0]['label']
            else:
                label = result['desc']
        except:
            code = -1
            label = '校验类型%s是否正确' % type
        return code, label

    def get_data(self):
        """
        1.完成图片二进制的读取
        2.完成头域的设置
        3.调用函数获取年龄、颜值、性别、接口接口的请求结果
        :return:
        """
        res = []
        # 调用__get_body方法完成图片二进制的读取
        data = self.__get_body()
        # 调用__get_header方法完成头域的设置
        headers = self.__get_header()
        # 调用完成年龄接口的请求，接口type：age
        code, age = self.__get_data_by_type('age', headers, data)
        res.append({'type': 'age', 'code': code, 'value': age})
        # 调用完成颜值接口的请求，接口type：face_score
        code, face_score = self.__get_data_by_type('face_score', headers, data)
        res.append({'type': 'face_score', 'code': code, 'value': face_score})
        # 调用完成性别接口的请求，接口type：sex
        code, sex = self.__get_data_by_type('sex', headers, data)
        res.append({'type': 'sex', 'code': code, 'value': sex})
        # 调用完成表情接口的请求，接口type：expression
        code, exp = self.__get_data_by_type('expression', headers, data)
        res.append({'type': 'exp', 'code': code, 'value': exp})
        print(res)
        return res

    def process_data(self, res):
        """
        1.解析参数res中的标签值，将其转换为对应的中文表达
        如，将性别的标签值’0‘转化为’男人‘
        :param res:服务器获取数据
        :return:
        """
        process_result = []
        for item in res:
            if item['type'] == 'age':
                if item['code'] == 0:  # 调用convert_age方法解析结果
                    item['value'] = FaceDesc(item['value']).convert_age()
                process_result.append({'type': '年龄', 'desc': item['value']})
            elif item['type'] == 'face_score':
                if item['code'] == 0:  # 调用convert_score方法解析结果
                    item['value'] = FaceDesc(item['value']).convert_score()
                    process_result.append({'type': '颜值', 'desc': item['value']})
            elif item['type'] == 'sex':
                if item['code'] == 0: # 调用convert_sex方法解析结果
                    item['value'] = FaceDesc(item['value']).convert_sex()
                process_result.append({'type': '性别', 'desc': item['value']})
            else:
                if item['code'] == 0: # 调用convert_expression方法解析结果
                    item['value'] = FaceDesc(item['value']).convert_expression()
                process_result.append({'type': '表情', 'desc': item['value']})
        return process_result

        return code, label

    # def face_web_analysis(self):
    #     """
    #     网络图片：人脸特征分析
    #     :return:
    #     """
    #     self.mode = 1
    #     # 调用__get_header方法完成图的头域的设置
    #     headers = self.__get_header()
    #     code, age = self.__get_data('age', headers)
    #     if code == 0:
    #         age = FaceDesc(age).convert_age()
    #     code, face_score = self.__get_data('face_score', headers)
    #     if code == 0:
    #         face_score = FaceDesc(face_score).convert_score()
    #     code, sex = self.__get_data('sex', headers)
    #     if code == 0:
    #         sex = FaceDesc(sex).convert_sex()
    #     code, exp = self.__get_data('expression', headers)
    #     if code == 0:
    #         exp = FaceDesc(exp).convert_expression()
    #     # print(self.msg % (age, face_score, sex, exp))

    def face_local_analysis(self):
        """
        本地图像：人脸特征识别
        :return: 特征分析结果
        """
        self.mode = 0
        # 调用get_data方法获取从服务器请求的数据
        request_data = self.get_data()
        # 调用process_data方法将数据进行解析
        process_data = self.process_data(request_data)
        return process_data


if __name__ == '__main__':
    APPID = "24b02ea1"  # 应用ID
    API_KEY = "0e0e46edc168862498c9b6ef141dcd3a"  # 接口密钥
    print(r'C:\\Users\\lenovo\\Desktop\\girl.jpg')
    res = FaceFeature(APPID, API_KEY, r'C:\\Users\\lenovo\\Desktop\\girl.jpg').face_local_analysis()
    print(res)
    # url = "http://hbimg.b0.upaiyun.com/a09289289df694cd6157f997ffa017cc44d4ca9e288fb-OehMYA_fw658"
    # FaceFeature(url).face_web_analysis()