import random
from datetime import datetime

import requests
import re
from bs4 import BeautifulSoup
import json
import time
import configparser
import os


session = requests.Session() # 設定 Session
config = configparser.ConfigParser()
isLoop = True

def main():
    login = "https://irs.zuvio.com.tw/irs/submitLogin"
    if not os.path.exists("config.ini"):
        account = input("請輸入學號：")
        password = input("請輸入密碼：")
        with open('config.ini', 'w') as f:
            config['user'] = {}
            config['user']['account'] = account
            config['user']['password'] = password
            config.write(f)
    config.read('config.ini')
    account = config['user']['account']
    password = config['user']['password']
    data = {
        'email': account + "@nkust.edu.tw",
        'password': password,
        'current_language': "zh-TW"
    }
    response = session.post(login, data=data)
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all("script", string=re.compile('var accessToken = "(.*?)";'))
        user_id = str(scripts[0]).split('var user_id = ')[1].split(";")[0]
        accessToken = str(scripts[0]).split('var accessToken = "')[1].split("\";")[0]
        courses(user_id, accessToken)
    except:
        print("登入失敗！")
        account = input("請輸入學號：")
        password = input("請輸入密碼：")
        with open('config.ini', 'w') as f:
            config['user'] = {}
            config['user']['account'] = account
            config['user']['password'] = password
            config.write(f)
        main()

signed_courses = set() # 存儲已簽到的課程

def courses(user_id, accessToken):
    url = f"https://irs.zuvio.com.tw/course/listStudentCurrentCourses?user_id={user_id}&accessToken={accessToken}"
    response = session.get(url)
    course_json = json.loads(response.content)
    if 'location' not in config.sections():
        print("看來你還沒有經緯度資訊，預設的經緯度會在楠梓校區的大仁樓")
        config['location'] = {}
        config['location']['lng'] = input('請輸入經度：')
        config['location']['lat'] = input('請輸入緯度：')
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    if course_json['status']: # 判斷資料獲取是否成功
        print(f"今天是 {datetime.today().strftime('%Y/%m/%d')}")
        print("這學期有修的課為：")
        for course_data in course_json['courses']:
            if "Zuvio" not in course_data['teacher_name']:  # 避免 Zuvio 官方活動之類的課程
                print(course_data['course_name'] + " - " + course_data['teacher_name'])
        already_checked = []
        while isLoop:
            has_course_available = False
            for course_data in course_json['courses']:
                if course_data in already_checked:
                    continue
                if "Zuvio" not in course_data['teacher_name']:
                    rollcall_id = check(course_data['course_id'])
                    if rollcall_id != "":
                        print(course_data['course_name'] + checkIn(user_id, accessToken, rollcall_id))
                        has_course_available = True
            already_checked.append(course_data)
            time.sleep(random.randint(1, 5))
            if not has_course_available:
                print(f"{datetime.today().strftime('%H:%M:%S')} 尚未有課程開放簽到", end='\r')


def check(course_ID):
    url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{course_ID}"
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    scripts = soup.find_all("script", string=re.compile("var rollcall_id = '(.*?)';"))
    rollcall_id = str(scripts[0]).split("var rollcall_id = '")[1].split("';")[0]
    return rollcall_id


def checkIn(user_id, accessToken, rollcall_id):
    url = "https://irs.zuvio.com.tw/app_v2/makeRollcall"
    # 預設經緯度為楠梓校區大仁樓
    lat = "22.725946571118374"
    lng = "120.31566086504968"
    if 'location' in config.sections() and config['location']['lng'] is not None and config['location']['lat'] is not None:
        lng = config['location']['lng']
        lat = config['location']['lat']
    data = {
        'user_id': user_id,
        'accessToken': accessToken,
        'rollcall_id': rollcall_id,
        'device': 'WEB',
        'lat': lat,
        'lng': lng
    }
    response = session.post(url, data=data)
    jsonres = json.loads(response.text)
    if jsonres['status']:
        return " - 簽到成功！"
    else:
        return " - 簽到失敗：" + jsonres['msg']


if __name__ == '__main__':
    main()
