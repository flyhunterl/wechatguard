import time
import pyautogui
import psutil
import win32gui
import win32process
import ctypes
import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import json
import hashlib

class WeChatGuardian:
    def __init__(self, idle_time=60):
        """
        微信窗口守护器
        :param idle_time: 空闲时间阈值（秒）
        """
        self.is_guarding = False
        self.idle_time_threshold = idle_time
        self.last_active_time = time.time()
        
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        """
        加载配置文件
        """
        default_config = {
            "password_enabled": False,
            "password": "",
            "idle_time": 60
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    return {**default_config, **saved_config}
            except Exception:
                return default_config
        
        return default_config

    def is_admin(self):
        """
        检查是否以管理员权限运行
        :return: 布尔值，是否为管理员
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def get_active_window_process(self):
        """
        获取当前活动窗口的进程名
        :return: 进程名称
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except Exception:
            return None

    def is_wechat_active(self):
        """
        检查微信是否为活动窗口
        :return: 布尔值
        """
        return self.get_active_window_process() == "WeChat.exe"

    def lock_wechat(self):
        """
        使用Ctrl+L锁定微信
        """
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

    def check_system_idle(self):
        """
        检查系统空闲时间
        :return: 布尔值，是否超过空闲阈值
        """
        current_time = time.time()
        idle_duration = current_time - self.last_active_time
        return idle_duration > self.idle_time_threshold

    def start_guardian(self):
        """
        开始守护模式
        """
        if not self.is_admin():
            print("请以管理员权限运行程序")
            return False

        self.is_guarding = True
        return True

    def stop_guardian(self, parent_window=None):
        """
        停止守护模式
        :param parent_window: 父窗口，用于显示密码输入对话框
        :return: 是否成功停止
        """
        # 检查是否启用密码保护且密码不为空
        if self.config.get("password_enabled", False) and self.config.get("password", ""):
            # 如果没有提供父窗口，创建一个临时的
            if parent_window is None:
                parent_window = tk.Tk()
                parent_window.withdraw()  # 隐藏主窗口

            # 弹出密码输入对话框
            input_password = simpledialog.askstring(
                "密码验证", 
                "请输入停止守护模式的密码:", 
                show='*', 
                parent=parent_window
            )

            # 验证密码
            stored_password = self.config.get("password", "")
            if not input_password or hashlib.sha256(input_password.encode()).hexdigest() != stored_password:
                messagebox.showerror("错误", "密码错误，无法停止守护模式")
                return False

        # 停止守护模式
        self.is_guarding = False
        return True

    def update_last_active_time(self):
        """
        更新最后活动时间
        """
        self.last_active_time = time.time()

    def run_guardian_cycle(self):
        """
        守护模式主循环
        """
        if not self.is_guarding:
            return

        if self.is_wechat_active():
            self.lock_wechat()
            return "😄😄😄嘿~你坏蛋。不要看我微信😄😄😄"

        if self.check_system_idle():
            self.lock_wechat()
            return "😄😄😄嘿~你坏蛋。不要看我微信😄😄😄"

        return None

# 示例使用
if __name__ == '__main__':
    guardian = WeChatGuardian(idle_time=60)
    guardian.start_guardian()
    
    while guardian.is_guarding:
        result = guardian.run_guardian_cycle()
        if result:
            print(result)
        time.sleep(2)  # 每2秒检查一次
