"""
Zuvio 自動簽到系統
重構版本 - 優化執行效率和可讀性
"""

import random
import json
import time
import os
import logging
import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import configparser


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zuvio.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class UserCredentials:
    """使用者憑證資料類別"""
    account: str
    password: str
    
    @property
    def email(self) -> str:
        """取得完整郵箱地址"""
        if '@' not in self.account:
            email = f"{self.account}@nkust.edu.tw"
            logger.info(f"自動加上預設網域：{email}")
            return email
        logger.info(f"使用完整郵箱地址：{self.account}")
        return self.account


@dataclass
class Location:
    """位置資訊資料類別"""
    latitude: str
    longitude: str


@dataclass
class AuthToken:
    """認證令牌資料類別"""
    user_id: str
    access_token: str


class ConfigManager:
    """配置管理類別"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self) -> None:
        """載入配置檔案"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
    
    def save_config(self) -> None:
        """儲存配置檔案"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_user_credentials(self) -> Optional[UserCredentials]:
        """取得使用者憑證"""
        if 'user' not in self.config.sections():
            return None
        
        user_section = self.config['user']
        return UserCredentials(
            account=user_section.get('account', ''),
            password=user_section.get('password', '')
        )
    
    def save_user_credentials(self, credentials: UserCredentials) -> None:
        """儲存使用者憑證"""
        if 'user' not in self.config.sections():
            self.config.add_section('user')
        
        self.config['user']['account'] = credentials.account
        self.config['user']['password'] = credentials.password
        self.save_config()
    
    def get_location(self) -> Optional[Location]:
        """取得位置資訊"""
        if 'location' not in self.config.sections():
            return None
        
        location_section = self.config['location']
        return Location(
            latitude=location_section.get('lat', ''),
            longitude=location_section.get('lng', '')
        )
    
    def save_location(self, location: Location) -> None:
        """儲存位置資訊"""
        if 'location' not in self.config.sections():
            self.config.add_section('location')
        
        self.config['location']['lat'] = location.latitude
        self.config['location']['lng'] = location.longitude
        self.save_config()


class AuthService:
    """認證服務類別"""
    
    def __init__(self):
        self.session = requests.Session()
        self.login_url = "https://irs.zuvio.com.tw/irs/submitLogin"
    
    def login(self, credentials: UserCredentials) -> Optional[AuthToken]:
        """執行登入"""
        try:
            data = {
                'email': credentials.email,
                'password': credentials.password,
                'current_language': "zh-TW"
            }
            
            logger.info("嘗試登入...")
            response = self.session.post(self.login_url, data=data)
            response.raise_for_status()
            
            return self._extract_tokens(response.content)
            
        except requests.RequestException as e:
            logger.error(f"登入請求失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"登入過程中發生錯誤: {e}")
            return None
    
    def _extract_tokens(self, html_content: bytes) -> Optional[AuthToken]:
        """從 HTML 回應中提取認證令牌"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            scripts = soup.find_all("script", string=re.compile('var accessToken = "(.*?)";'))
            
            if not scripts:
                logger.error("無法找到認證令牌")
                return None
            
            script_content = str(scripts[0])
            user_id = script_content.split('var user_id = ')[1].split(";")[0].strip('"')
            access_token = script_content.split('var accessToken = "')[1].split("\";")[0]
            
            logger.info("成功取得認證令牌")
            return AuthToken(user_id=user_id, access_token=access_token)
            
        except Exception as e:
            logger.error(f"提取認證令牌失敗: {e}")
            return None


class CourseService:
    """課程管理服務類別"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.signed_courses: set = set()
    
    def get_courses(self, auth_token: AuthToken) -> Optional[List[Dict]]:
        """取得課程清單"""
        try:
            url = f"https://irs.zuvio.com.tw/course/listStudentCurrentCourses?user_id={auth_token.user_id}&accessToken={auth_token.access_token}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            course_data = response.json()
            
            if not course_data.get('status'):
                logger.error("取得課程資料失敗")
                return None
            
            # 過濾掉 Zuvio 官方活動
            valid_courses = [
                course for course in course_data.get('courses', [])
                if "Zuvio" not in course.get('teacher_name', '')
            ]
            
            logger.info(f"成功取得 {len(valid_courses)} 門課程")
            return valid_courses
            
        except requests.RequestException as e:
            logger.error(f"取得課程資料請求失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析課程資料失敗: {e}")
            return None
    
    def check_rollcall_availability(self, course_id: str) -> Optional[str]:
        """檢查課程是否有開放簽到"""
        try:
            url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{course_id}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all("script", string=re.compile("var rollcall_id = '(.*?)';"))
            
            if not scripts:
                return None
            
            script_content = str(scripts[0])
            rollcall_id = script_content.split("var rollcall_id = '")[1].split("';")[0]
            
            return rollcall_id if rollcall_id else None
            
        except Exception as e:
            logger.error(f"檢查簽到可用性失敗 (課程ID: {course_id}): {e}")
            return None
    
    def perform_checkin(self, auth_token: AuthToken, rollcall_id: str, location: Location) -> Tuple[bool, str]:
        """執行簽到"""
        try:
            url = "https://irs.zuvio.com.tw/app_v2/makeRollcall"
            
            data = {
                'user_id': auth_token.user_id,
                'accessToken': auth_token.access_token,
                'rollcall_id': rollcall_id,
                'device': 'WEB',
                'lat': location.latitude,
                'lng': location.longitude
            }
            
            response = self.session.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status'):
                logger.info(f"簽到成功 (Rollcall ID: {rollcall_id})")
                return True, "簽到成功！"
            else:
                error_msg = result.get('msg', '未知錯誤')
                logger.warning(f"簽到失敗: {error_msg}")
                return False, f"簽到失敗：{error_msg}"
                
        except requests.RequestException as e:
            logger.error(f"簽到請求失敗: {e}")
            return False, f"簽到請求失敗：{e}"
        except json.JSONDecodeError as e:
            logger.error(f"解析簽到回應失敗: {e}")
            return False, f"解析簽到回應失敗：{e}"


class ZuvioAutoChecker:
    """Zuvio 自動簽到主類別"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.auth_service = AuthService()
        self.course_service = None
        self.running = True
    
    def setup_user_credentials(self) -> UserCredentials:
        """設定使用者憑證"""
        credentials = self.config_manager.get_user_credentials()
        
        if not credentials:
            print("首次使用，請設定您的帳號資訊")
            account = input("請輸入完整帳號（例如：學號@學校網域 或完整郵箱）：")
            password = input("請輸入密碼：")
            
            credentials = UserCredentials(account=account, password=password)
            self.config_manager.save_user_credentials(credentials)
        
        return credentials
    
    def setup_location(self) -> Location:
        """設定位置資訊"""
        location = self.config_manager.get_location()
        
        if not location:
            print("首次使用，請設定您的位置資訊")
            print("預設位置為楠梓校區大仁樓")
            
            lng = input('請輸入經度（直接按 Enter 使用預設值 120.31566086504968）：')
            lat = input('請輸入緯度（直接按 Enter 使用預設值 22.725946571118374）：')
            
            location = Location(
                longitude=lng or "120.31566086504968",
                latitude=lat or "22.725946571118374"
            )
            
            self.config_manager.save_location(location)
        
        return location
    
    def display_courses(self, courses: List[Dict]) -> None:
        """顯示課程清單"""
        print(f"今天是 {datetime.today().strftime('%Y/%m/%d')}")
        print("這學期有修的課為：")
        
        for course in courses:
            print(f"{course['course_name']} - {course['teacher_name']}")
    
    def run_checkin_loop(self, auth_token: AuthToken, courses: List[Dict], location: Location) -> None:
        """執行簽到迴圈"""
        already_checked = []
        
        while self.running:
            has_course_available = False
            
            for course in courses:
                if course in already_checked:
                    continue
                
                rollcall_id = self.course_service.check_rollcall_availability(course['course_id'])
                
                if rollcall_id:
                    success, message = self.course_service.perform_checkin(
                        auth_token, rollcall_id, location
                    )
                    
                    print(f"{course['course_name']} - {message}")
                    has_course_available = True
                    
                    # 將已簽到的課程加入已檢查清單
                    already_checked.append(course)
            
            if not has_course_available:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"{current_time} 尚未有課程開放簽到", end='\r')
            
            # 隨機等待 1-5 秒
            time.sleep(random.randint(1, 5))
    
    def run(self) -> None:
        """執行主程式"""
        try:
            logger.info("啟動 Zuvio 自動簽到系統")
            
            # 設定使用者憑證
            credentials = self.setup_user_credentials()
            
            # 設定位置資訊
            location = self.setup_location()
            
            # 執行登入
            auth_token = self.auth_service.login(credentials)
            if not auth_token:
                print("登入失敗！請檢查您的帳號密碼是否正確")
                
                # 重新設定憑證
                print("請重新輸入帳號資訊")
                account = input("請輸入完整帳號：")
                password = input("請輸入密碼：")
                
                new_credentials = UserCredentials(account=account, password=password)
                self.config_manager.save_user_credentials(new_credentials)
                
                # 重新執行
                return self.run()
            
            # 初始化課程服務
            self.course_service = CourseService(self.auth_service.session)
            
            # 取得課程清單
            courses = self.course_service.get_courses(auth_token)
            if not courses:
                print("無法取得課程資料")
                return
            
            # 顯示課程清單
            self.display_courses(courses)
            
            # 開始簽到迴圈
            print("\n開始監控簽到...")
            self.run_checkin_loop(auth_token, courses, location)
            
        except KeyboardInterrupt:
            logger.info("使用者中斷程式")
            print("\n程式已停止")
        except Exception as e:
            logger.error(f"程式執行過程中發生未預期的錯誤: {e}")
            print(f"程式執行失敗：{e}")


def main():
    """主函數"""
    app = ZuvioAutoChecker()
    app.run()


if __name__ == '__main__':
    main()