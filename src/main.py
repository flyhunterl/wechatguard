import os
import sys
import threading
import time
import logging
import win32gui
import win32con
import win32api
from PIL import Image
import tkinter as tk
from tkinter import messagebox

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 改为 INFO 级别，减少调试信息
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('wechat_guardian.log', encoding='utf-8'),  # 文件处理器
        # 移除控制台处理器，避免干扰计时显示
    ]
)

# 添加一个测试日志
logging.info("程序启动")

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.icon_generator import IconGenerator
from src.wechat_guardian import WeChatGuardian
from src.settings import GuardianSettings
from src.help_window import HelpWindow

class WeChatGuardianApp:
    WM_TRAYICON = win32con.WM_USER + 20
    
    def __init__(self):
        logging.info("初始化微信守护程序")
        self.guardian = WeChatGuardian()
        self.settings = GuardianSettings()
        
        # 添加配置更新回调
        self.settings.on_config_changed = self.on_config_changed
        
        # 加载图标
        self.gray_icon = IconGenerator.create_icon('gray')
        self.green_icon = IconGenerator.create_icon('green')
        
        # 创建隐藏窗口用于接收系统托盘消息
        self.wc = win32gui.WNDCLASS()
        self.wc.lpfnWndProc = self.wnd_proc
        self.wc.lpszClassName = "WeChatGuardianTrayClass"
        win32gui.RegisterClass(self.wc)
        
        self.hwnd = win32gui.CreateWindow(
            self.wc.lpszClassName, 
            "WeChatGuardian", 
            0, 0, 0, 0, 0, 
            0, 0, 0, None
        )
        
        # 创建系统托盘图标并保存句柄
        self.icon_handle = self.create_tray_icon()
        
        # 立即启动守护线程，开始检测空闲时间
        threading.Thread(target=self.guardian_thread, daemon=True).start()

    def create_tray_icon(self):
        """
        创建系统托盘图标
        """
        # 创建临时图标文件
        temp_icon_path = os.path.join(os.path.dirname(__file__), 'temp_gray_icon.ico')
        self.gray_icon.save(temp_icon_path, format='ICO', sizes=[(16, 16)])
        
        # 加载图标
        hicon = win32gui.LoadImage(
            0, 
            temp_icon_path, 
            win32con.IMAGE_ICON, 
            16, 16, 
            win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTCOLOR
        )
        
        # 删除临时文件
        os.remove(temp_icon_path)
        
        # 创建托盘图标
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, self.WM_TRAYICON, hicon, "微信守护程序")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        
        return nid  # 返回图标句柄

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        """
        窗口消息处理程序
        """
        if msg == self.WM_TRAYICON:
            if lparam == win32con.WM_LBUTTONDBLCLK:
                logging.info("系统托盘图标双击，尝试启动守护模式")
                self.start_guardian()
            elif lparam == win32con.WM_RBUTTONUP:
                menu = win32gui.CreatePopupMenu()
                win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "开始守护")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 2, "停止守护")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 3, "设置")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 4, "帮助")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 5, "退出")
                pos = win32gui.GetCursorPos()
                win32gui.SetForegroundWindow(self.hwnd)
                result = win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN | win32con.TPM_LEFTBUTTON | win32con.TPM_BOTTOMALIGN | win32con.TPM_RETURNCMD, pos[0], pos[1], 0, self.hwnd, None)
                win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
                if result == 1:
                    self.start_guardian()
                elif result == 2:
                    self.stop_guardian()
                elif result == 3:
                    self.open_settings()
                elif result == 4:
                    self.show_help()
                elif result == 5:
                    self.exit_app()
        
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def start_guardian(self):
        """
        开始守护模式
        """
        logging.info("尝试开始守护模式")
        if not self.guardian.is_admin():
            return False

        if self.guardian.is_guarding:
            return False

        if self.guardian.start_guardian():
            # 更新图标为绿色
            temp_icon_path = os.path.join(os.path.dirname(__file__), 'temp_green_icon.ico')
            self.green_icon.save(temp_icon_path, format='ICO', sizes=[(16, 16)])
            hicon = win32gui.LoadImage(
                0, 
                temp_icon_path, 
                win32con.IMAGE_ICON, 
                16, 16, 
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTCOLOR
            )
            os.remove(temp_icon_path)
            
            flags = win32gui.NIF_ICON
            nid = (self.hwnd, 0, flags, self.WM_TRAYICON, hicon)
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
            
            threading.Thread(target=self.guardian_thread, daemon=True).start()
            logging.info("守护模式已启动")
            return True
        
        return False

    def stop_guardian(self):
        """
        停止守护模式
        """
        logging.info("停止守护模式")
        
        # 创建一个临时的 Tk 窗口用于密码验证
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 尝试停止守护模式，传入父窗口
        if self.guardian.stop_guardian(parent_window=root):
            # 恢复灰色图标
            temp_icon_path = os.path.join(os.path.dirname(__file__), 'temp_gray_icon.ico')
            self.gray_icon.save(temp_icon_path, format='ICO', sizes=[(16, 16)])
            hicon = win32gui.LoadImage(
                0, 
                temp_icon_path, 
                win32con.IMAGE_ICON, 
                16, 16, 
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTCOLOR
            )
            os.remove(temp_icon_path)
            
            flags = win32gui.NIF_ICON
            nid = (self.hwnd, 0, flags, self.WM_TRAYICON, hicon)
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
            
            # 关闭临时窗口
            root.destroy()

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
        退出应用程序
        """
        # 移除系统托盘图标
        if hasattr(self, 'icon_handle'):
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self.icon_handle)
        
        # 退出程序
        win32gui.PostQuitMessage(0)

    def guardian_thread(self):
        """
        守护线程
        """
        print("\n" * 2)
        print("开始监控系统空闲时间...")
        print("=" * 50)
        
        while True:
            try:
                # 只在非守护模式下检测空闲时间
                if not self.guardian.is_guarding:
                    # 获取并显示空闲时间
                    idle_time = self.guardian.get_idle_duration()
                    print(f"\r当前空闲时间：{idle_time:.1f}秒，设定阈值：{self.guardian.idle_time_threshold}秒", end='', flush=True)
                    
                    # 检查是否需要进入守护模式
                    if idle_time > self.guardian.idle_time_threshold:
                        print(f"\n系统已空闲 {idle_time:.1f} 秒，进入守护模式！")
                        print("=" * 50)
                        self.guardian.is_guarding = True
                        # 更新图标为绿色
                        temp_icon_path = os.path.join(os.path.dirname(__file__), 'temp_green_icon.ico')
                        self.green_icon.save(temp_icon_path, format='ICO', sizes=[(16, 16)])
                        hicon = win32gui.LoadImage(
                            0, 
                            temp_icon_path, 
                            win32con.IMAGE_ICON, 
                            16, 16, 
                            win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTCOLOR
                        )
                        os.remove(temp_icon_path)
                        
                        flags = win32gui.NIF_ICON
                        nid = (self.hwnd, 0, flags, self.WM_TRAYICON, hicon)
                        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
                
                # 在守护模式下只检查微信窗口
                elif self.guardian.is_wechat_active():
                    self.guardian.lock_wechat()
                    self.guardian.is_guarding = False
                    # 更新图标为灰色
                    temp_icon_path = os.path.join(os.path.dirname(__file__), 'temp_gray_icon.ico')
                    self.gray_icon.save(temp_icon_path, format='ICO', sizes=[(16, 16)])
                    hicon = win32gui.LoadImage(
                        0, 
                        temp_icon_path, 
                        win32con.IMAGE_ICON, 
                        16, 16, 
                        win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTCOLOR
                    )
                    os.remove(temp_icon_path)
                    
                    flags = win32gui.NIF_ICON
                    nid = (self.hwnd, 0, flags, self.WM_TRAYICON, hicon)
                    win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
                    
                    messagebox.showwarning("警告", "😄😄😄嘿~你坏蛋。不要看我微信😄😄😄")
                    print("\n" * 2)
                    print("继续监控系统空闲时间...")
                    print("=" * 50)
                
                time.sleep(0.1)  # 缩短检测间隔，使显示更流畅
                
            except Exception as e:
                logging.error(f"守护线程错误: {str(e)}")
                logging.exception(e)

    def on_config_changed(self, new_config):
        """
        处理配置更新
        """
        if self.guardian:
            self.guardian.config = new_config
            self.guardian.idle_time_threshold = new_config.get("idle_time", 60)

    def run(self):
        """
        运行应用程序
        """
        if not self.guardian.is_admin():
            logging.error("未以管理员权限运行")
            messagebox.showerror("错误", "请以管理员权限运行程序")
            return

        # 消息循环
        win32gui.PumpMessages()

def main():
    try:
        app = WeChatGuardianApp()
        app.run()
    except Exception as e:
        logging.critical(f"程序启动失败: {e}")
        print(f"程序启动失败: {e}")

if __name__ == '__main__':
    main()
