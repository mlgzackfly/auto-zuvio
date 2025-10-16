"""
Simple secure input utilities
"""

import getpass
import os


def get_hidden_password(prompt: str = "請輸入密碼: ") -> str:
    """Get hidden password input from user"""
    return getpass.getpass(prompt)


def set_file_permissions(file_path: str):
    """Set restricted file permissions (owner read/write only)"""
    if os.path.exists(file_path):
        os.chmod(file_path, 0o600)


def create_secure_config():
    """Create a simple secure configuration setup"""
    import configparser
    
    config = configparser.ConfigParser()
    
    if os.path.exists("config.ini"):
        config.read("config.ini", encoding='utf-8')
        # Backup existing config
        import shutil
        shutil.copy("config.ini", "config.ini.backup")
        print("現有配置已備份為 config.ini.backup")
    
    # Setup user credentials with hidden input
    if 'user' not in config.sections():
        config.add_section('user')
    
    account = input("請輸入完整帳號: ")
    password = get_hidden_password("請輸入密碼: ")
    
    config['user']['account'] = account
    config['user']['password'] = password
    
    # Setup location if needed
    if 'location' not in config.sections():
        config.add_section('location')
        print("請設定位置資訊（直接按 Enter 使用預設值）")
        lng = input("請輸入經度（預設: 120.31566086504968）: ")
        lat = input("請輸入緯度（預設: 22.725946571118374）: ")
        
        config['location']['lng'] = lng or "120.31566086504968"
        config['location']['lat'] = lat or "22.725946571118374"
    
    # Save with restricted permissions
    with open("config.ini", 'w', encoding='utf-8') as f:
        config.write(f)
    
    set_file_permissions("config.ini")
    print("配置已儲存，檔案權限已設定為僅所有者可存取")


if __name__ == "__main__":
    create_secure_config()
