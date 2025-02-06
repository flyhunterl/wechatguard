import requests
import json
import logging
import webbrowser
from tkinter import messagebox
from packaging import version
import threading

class Updater:
    def __init__(self):
        self.current_version = "0.3.4"  # 更新版本号
        self.github_api = "https://api.github.com/repos/flyhunterl/wechatguard/releases/latest"
        self.github_releases = "https://github.com/flyhunterl/wechatguard/releases/latest"

    def check_update(self):
        """
        检查更新
        返回: (是否有更新, 最新版本号, 更新说明)
        """
        try:
            response = requests.get(self.github_api, timeout=5)
            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info['tag_name'].lstrip('v')
                
                if version.parse(latest_version) > version.parse(self.current_version):
                    return True, latest_version, release_info['body']
            
            return False, self.current_version, ""
            
        except Exception as e:
            logging.error(f"检查更新失败: {str(e)}")
            return False, self.current_version, ""

    def show_update_dialog(self):
        """
        显示更新提示对话框
        """
        has_update, latest_version, release_notes = self.check_update()
        
        if has_update:
            message = f"""发现新版本！
当前版本: v{self.current_version}
最新版本: v{latest_version}

更新内容:
{release_notes}

是否前往下载页面？"""
            
            if messagebox.askyesno("发现新版本", message):
                webbrowser.open(self.github_releases)
        
        return has_update

def check_update_async(root):
    """
    异步检查更新
    """
    def check_update():
        try:
            # 当前版本
            current_version = "0.3.4"  # 更新当前版本号
            
            # 获取最新版本
            response = requests.get(
                "https://raw.githubusercontent.com/flyhunterl/wechatguard/main/version.txt",
                timeout=5
            )
            latest_version = response.text.strip()
            
            # 比较版本号
            if version.parse(latest_version) > version.parse(current_version):
                if messagebox.askyesno(
                    "发现新版本", 
                    f"当前版本：{current_version}\n" +
                    f"最新版本：{latest_version}\n\n" +
                    "是否前往下载？"
                ):
                    webbrowser.open("https://github.com/flyhunterl/wechatguard/releases")
        except Exception as e:
            logging.error(f"检查更新失败: {str(e)}")
    
    threading.Thread(target=check_update, daemon=True).start() 