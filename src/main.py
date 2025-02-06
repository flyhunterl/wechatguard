import os
import sys
import threading
import time
import pystray
from PIL import Image
import tkinter as tk
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='wechat_guardian.log',
    filemode='w'
)

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.icon_generator import IconGenerator
from src.wechat_guardian import WeChatGuardian
from src.settings import GuardianSettings
from src.help_window import HelpWindow

class WeChatGuardianApp:
    def __init__(self):
        logging.info("初始化微信守护程序")
        self.guardian = WeChatGuardian()
        self.settings = GuardianSettings()
        
        # 加载图标
        self.gray_icon = IconGenerator.create_icon('gray')
        self.green_icon = IconGenerator.create_icon('green')
        
        # 创建系统托盘图标
        try:
            self.icon = pystray.Icon(
                "WeChatGuardian", 
                self.gray_icon, 
                "微信守护程序"
            )
            
            # 配置托盘菜单
            self.icon.menu = pystray.Menu(
                pystray.MenuItem("开始守护", self.start_guardian),
                pystray.MenuItem("停止守护", self.stop_guardian),
                pystray.MenuItem("设置", self.open_settings),
                pystray.MenuItem("帮助", self.show_help),
                pystray.MenuItem("退出", self.exit_app)
            )
            logging.info("系统托盘图标创建成功")
        except Exception as e:
            logging.error(f"创建系统托盘图标失败: {e}")
            raise

    def start_guardian(self):
        """
        开始守护模式
        """
        logging.info("尝试开始守护模式")
        if self.guardian.start_guardian():
            self.icon.icon = self.green_icon
            threading.Thread(target=self.guardian_thread, daemon=True).start()
            logging.info("守护模式已启动")

    def stop_guardian(self):
        """
        停止守护模式
        """
        logging.info("停止守护模式")
        self.guardian.stop_guardian()
        self.icon.icon = self.gray_icon

    def open_settings(self):
        """
        打开设置界面
        """
        logging.info("打开设置界面")
        self.settings.open_settings_window()

    def show_help(self):
        """
        显示帮助窗口
        """
        logging.info("显示帮助窗口")
        HelpWindow.show_help()

    def exit_app(self):
        """
        退出程序
        """
        logging.info("退出程序")
        self.stop_guardian()
        self.icon.stop()

    def guardian_thread(self):
        """
        守护线程
        """
        logging.info("守护线程启动")
        while self.guardian.is_guarding:
            result = self.guardian.run_guardian_cycle()
            if result:
                # 弹出警告消息
                logging.warning(f"触发守护: {result}")
                tk.messagebox.showwarning("警告", result)
                self.stop_guardian()
                break
            time.sleep(2)

    def run(self):
        """
        运行应用程序
        """
        if not self.guardian.is_admin():
            logging.error("未以管理员权限运行")
            tk.messagebox.showerror("错误", "请以管理员权限运行程序")
            return

        logging.info("启动微信守护程序")
        self.icon.run()

def main():
    try:
        app = WeChatGuardianApp()
        app.run()
    except Exception as e:
        logging.critical(f"程序启动失败: {e}")
        print(f"程序启动失败: {e}")

if __name__ == '__main__':
    main()
