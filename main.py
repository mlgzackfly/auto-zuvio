import random
from datetime import datetime

import requests
import re
from bs4 import BeautifulSoup
import json
import time
import configparser
import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QThread
from ui import Ui_MainWindow

session = requests.Session()  # 設定 Session
config = configparser.ConfigParser()


def checkIn(user_id, accessToken, rollcall_id):
    url = "https://irs.zuvio.com.tw/app_v2/makeRollcall"
    # 經緯度為楠梓校區大仁樓
    lat = "22.725946571118374"
    lng = "120.31566086504968"
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
    elif jsonres['msg'] == "ROLLCALL IS ANSWERED":
        return " - 簽到失敗：已經簽過了！"
    else:
        return "- 簽到失敗：" + jsonres['msg']


def check(course_ID):
    url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{course_ID}"
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    scripts = soup.find_all("script", string=re.compile("var rollcall_id = '(.*?)';"))
    rollcall_id = str(scripts[0]).split("var rollcall_id = '")[1].split("';")[0]
    return rollcall_id


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.loginButton.clicked.connect(self.login)
        self.ui.exitButton.clicked.connect(self.exit)
        if not os.path.exists("config.ini"):
            account = self.ui.accountInput
            password = self.ui.passwordInput
            with open('config.ini', 'w') as f:
                config['user'] = {}
                config['user']['account'] = account
                config['user']['password'] = password
                config.write(f)
        config.read('config.ini')
        self.account = config['user']['account']
        self.password = config['user']['password']
        self.ui.accountInput.setText(config['user']['account'])
        self.ui.passwordInput.setText(config['user']['password'])

    def login(self):
        login = "https://irs.zuvio.com.tw/irs/submitLogin"
        data = {
            'email': self.account + "@nkust.edu.tw",
            'password': self.password,
            'current_language': "zh-TW"
        }
        response = session.post(login, data=data)
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all("script", string=re.compile('var accessToken = "(.*?)";'))
            user_id = str(scripts[0]).split('var user_id = ')[1].split(";")[0]
            accessToken = str(scripts[0]).split('var accessToken = "')[1].split("\";")[0]
            self.courses(user_id, accessToken)
        except Exception as e:
            print("登入失敗！")
            self.ui.outputMsg.setText(e)

    def exit(self):
        sys.exit(app.exec())

    def courses(self, user_id, accessToken):
        url = f"https://irs.zuvio.com.tw/course/listStudentCurrentCourses?user_id={user_id}&accessToken={accessToken}"
        response = session.get(url)
        course_json = json.loads(response.content)
        if course_json['status']:  # 判斷資料獲取是否成功
            print(f"今天是 {datetime.today().strftime('%Y/%m/%d')}")
            print("這學期有修的課為：")
            for course_data in course_json['courses']:
                if "Zuvio" not in course_data['teacher_name']:  # 避免 Zuvio 官方活動之類的課程
                    print(course_data['course_name'] + " - " + course_data['teacher_name'])
                    self.ui.courseList.append(course_data['course_name'] + " - " + course_data['teacher_name'])

            self.ui.loginButton.setEnabled(0)

            while True:
                for course_data in course_json['courses']:
                    if "Zuvio" not in course_data['teacher_name']:  # 避免 Zuvio 官方活動之類的課程
                        rollcall_id = check(course_data['course_id'])
                        if rollcall_id != "":  # rollcall_id 不為空的話代表可以簽到
                            print(course_data['course_name'] + checkIn(user_id, accessToken, rollcall_id))
                            self.ui.outputMsg.setText(
                                course_data['course_name'] + checkIn(user_id, accessToken, rollcall_id))
                            QApplication.processEvents()
                self.ui.outputMsg.setText(f"{datetime.today().strftime('%H:%M:%S')} 尚未有課程開放簽到")
                QApplication.processEvents()
                print(f"{datetime.today().strftime('%H:%M:%S')} 尚未有課程開放簽到")
        else:
            self.ui.outputMsg.setText("Zuvio 出錯！")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
