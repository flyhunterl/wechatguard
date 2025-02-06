import time
import pyautogui
import psutil
import win32gui
import win32process
import ctypes

class WeChatGuardian:
    def __init__(self, idle_time=60):
        """
        微信窗口守护器
        :param idle_time: 空闲时间阈值（秒）
        """
        self.is_guarding = False
        self.idle_time_threshold = idle_time
        self.last_active_time = time.time()

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

    def stop_guardian(self, password=None):
        """
        停止守护模式
        :param password: 可选的停止密码
        :return: 是否成功停止
        """
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
