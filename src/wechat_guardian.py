import time
import pyautogui
import psutil
import win32gui
import win32process
import ctypes
import win32api
import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import json
import hashlib
import logging
import base64
from src.settings import GuardianSettings

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_uint),
    ]

class WeChatGuardian:
    def __init__(self, root=None):
        """
        微信窗口守护器
        :param root: 主窗口
        """
        self.root = root
        self.is_guarding = False
        self.idle_time_threshold = 60
        self.last_input_info = LASTINPUTINFO()
        self.last_input_info.cbSize = ctypes.sizeof(self.last_input_info)
        
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.settings = GuardianSettings()  # 创建 settings 实例
        self.config = self.settings.config  # 使用 settings 的配置
        self.idle_time_threshold = self.config.get("idle_time", 60)

    def load_config(self, config_path):
        """
        加载配置文件
        """
        default_config = {
            "password_enabled": False,
            "password": "",
            "idle_time": 10,  # 修改默认值为10秒
            "salt": ""
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

    def get_idle_duration(self):
        """
        获取系统空闲时间（秒）
        """
        try:
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
            millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0
        except Exception as e:
            print(f"\n获取空闲时间失败: {str(e)}")
            return 0

    def check_system_idle(self):
        """
        检查系统空闲时间
        """
        idle_duration = self.get_idle_duration()
        is_idle = idle_duration > self.idle_time_threshold
        logging.debug(f"空闲时间: {idle_duration:.1f}秒, 阈值: {self.idle_time_threshold}秒, 是否空闲: {is_idle}")
        
        # 如果空闲，再次确认
        if is_idle:
            logging.info(f"检测到系统空闲，准备进入守护模式...")
            time.sleep(0.5)  # 短暂等待以确认
            second_check = self.get_idle_duration()
            is_still_idle = second_check > self.idle_time_threshold
            if is_still_idle:
                logging.info("确认空闲状态，正在启动守护...")
                self.start_guardian()  # 自动启动守护模式
            return is_still_idle
        
        return is_idle

    def start_guardian(self):
        """
        开始守护模式
        """
        if not self.is_admin():
            logging.error("请以管理员权限运行程序")
            return False

        self.is_guarding = True
        logging.info(f"开始守护模式，空闲时间阈值：{self.idle_time_threshold}秒")
        return True

    def stop_guardian(self, manual=False):
        """
        停止守护模式
        
        Args:
            manual (bool): 是否是手动停止，如果是手动停止需要验证密码
        
        Returns:
            bool: 是否成功停止守护
        """
        logging.info(f"停止守护 (手动: {manual})")
        
        # 如果是手动停止且启用了密码保护，需要验证密码
        if manual and self.config.get('password'):
            password = simpledialog.askstring(
                "验证密码",
                "请输入密码:",
                parent=self.root,
                show='*'
            )
            if not password or not self.verify_password(password):
                messagebox.showerror("错误", "密码验证失败")
                return False
        
        self.is_guarding = False
        logging.info("守护已停止")
        return True

    def update_last_active_time(self):
        """
        更新最后活动时间
        """
        self.last_input_info.dwTime = ctypes.windll.kernel32.GetTickCount()
        logging.debug(f"更新最后活动时间: {time.strftime('%H:%M:%S', time.localtime(self.last_input_info.dwTime / 1000))}")

    def run_guardian_cycle(self):
        """
        守护模式主循环
        """
        try:
            # 获取当前空闲时间
            idle_time = self.get_idle_duration()
            
            # 不在守护模式下，检查是否需要进入守护模式
            if not self.is_guarding:
                if idle_time > self.idle_time_threshold:
                    print(f"\n系统已空闲 {idle_time:.1f} 秒，进入守护模式！")
                    self.is_guarding = True
                    return "START_GUARDIAN"
                return None
            
            # 在守护模式下，检查微信窗口
            if self.is_wechat_active():
                self.lock_wechat()
                self.is_guarding = False
                return "😄😄😄嘿~你坏蛋。不要看我微信😄😄😄"

        except Exception as e:
            logging.error(f"守护循环错误: {str(e)}")
            logging.exception(e)
        
        return None

    def verify_password(self, password):
        """
        验证密码
        """
        try:
            if not self.config.get('password'):
                return True
            
            stored_hash = base64.b64decode(self.config['password'].encode('utf-8'))
            stored_salt = base64.b64decode(self.config['salt'].encode('utf-8'))
            
            input_hash = self._hash_password(password, stored_salt)
            
            # 使用安全的比较方法
            return self._secure_compare(stored_hash, input_hash)
        except Exception as e:
            logging.error(f"密码验证失败: {str(e)}")
            return False

    def _hash_password(self, password, salt):
        # 实现密码哈希函数
        pass

    def _secure_compare(self, stored_hash, input_hash):
        # 实现安全的比较函数
        pass

# 示例使用
if __name__ == '__main__':
    guardian = WeChatGuardian()
    guardian.start_guardian()
    
    while guardian.is_guarding:
        result = guardian.run_guardian_cycle()
        if result:
            print(result)
        time.sleep(2)  # 每2秒检查一次
