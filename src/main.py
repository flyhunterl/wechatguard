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
from tkinter import messagebox, ttk, simpledialog
from src.updater import check_update_async

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
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

from src.icon_generator import IconGenerator
from src.wechat_guardian import WeChatGuardian
from src.settings import GuardianSettings
from src.help_window import HelpWindow

class WeChatGuardianApp:
    WM_TRAYICON = win32con.WM_USER + 20
    
    def __init__(self):
        logging.info("初始化微信守护程序")
        
        # 定义窗口类名
        self.window_class_name = "WeChatGuardianTrayClass"
        
        # 创建隐藏的主窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        
        # 初始化组件
        self.guardian = WeChatGuardian(self.root)
        self.settings = GuardianSettings()
        
        # 注册窗口类
        self.register_window_class()
        
        # 创建系统托盘图标
        self.create_tray_icon()
        
        # 检查更新
        check_update_async(self.root)
        
        # 启动守护线程
        self.start_guardian_thread()
        
        # 进入消息循环
        self.root.mainloop()

    def register_window_class(self):
        """
        注册窗口类
        """
        self.wc = win32gui.WNDCLASS()
        self.wc.lpfnWndProc = self.wnd_proc
        self.wc.lpszClassName = self.window_class_name
        self.wc.hInstance = win32gui.GetModuleHandle(None)
        self.class_atom = win32gui.RegisterClass(self.wc)
        
        # 创建隐藏窗口
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            self.window_class_name,
            win32con.WS_OVERLAPPED,
            0, 0, 0, 0,
            0, 0, self.wc.hInstance, None
        )
        
        # 添加配置更新回调
        self.settings.on_config_changed = self.on_config_changed
        
        # 加载图标
        self.gray_icon = IconGenerator.create_icon('gray')
        self.green_icon = IconGenerator.create_icon('green')

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
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
        elif msg == self.WM_TRAYICON:
            if lparam == win32con.WM_LBUTTONDBLCLK:
                logging.info("系统托盘图标双击，尝试启动守护模式")
                self.start_guardian()
            elif lparam == win32con.WM_RBUTTONUP:
                menu = win32gui.CreatePopupMenu()
                win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "开始守护")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 2, "停止守护")
                win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 3, "设置")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 4, "帮助")
                win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 5, "退出")
                
                pos = win32gui.GetCursorPos()
                win32gui.SetForegroundWindow(hwnd)
                id = win32gui.TrackPopupMenu(
                    menu,
                    win32con.TPM_LEFTALIGN | win32con.TPM_BOTTOMALIGN | win32con.TPM_RETURNCMD,
                    pos[0], pos[1],
                    0,
                    hwnd,
                    None
                )
                win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
                
                if id == 1:  # 开始守护
                    self.start_guardian()
                elif id == 2:  # 停止守护
                    logging.info("尝试停止守护")
                    try:
                        result = self.stop_guardian()
                        logging.info(f"停止守护结果: {result}")
                    except Exception as e:
                        logging.error(f"停止守护失败: {str(e)}")
                        logging.exception(e)
                elif id == 3:  # 设置
                    self.settings.show_settings_dialog()
                elif id == 4:  # 帮助
                    HelpWindow()
                elif id == 5:  # 退出
                    if self.verify_exit():  # 添加退出验证
                        self.cleanup()
                        win32gui.DestroyWindow(hwnd)
                        self.root.quit()
                        return 0
                
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def verify_exit(self):
        """
        验证退出操作
        """
        # 如果启用了密码保护，需要验证密码
        if self.settings.config.get('password'):
            password = simpledialog.askstring(
                "验证密码",
                "请输入密码:",
                parent=self.root,
                show='*'
            )
            if not password or not self.settings.verify_password(password):
                messagebox.showerror("错误", "密码验证失败")
                return False
        
        # 确认是否退出
        if messagebox.askyesno("确认", "确定要退出程序吗？"):
            return True
        return False

    def cleanup(self):
        """
        清理资源
        """
        try:
            logging.info("开始清理资源")
            # 移除系统托盘图标
            nid = (self.hwnd, 0)
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
            
            # 停止所有线程
            self.guardian.is_guarding = False
            
            # 删除临时文件
            if os.path.exists('temp_gray_icon.ico'):
                os.remove('temp_gray_icon.ico')
            if os.path.exists('temp_green_icon.ico'):
                os.remove('temp_green_icon.ico')
            
            logging.info("程序正常退出")
        except Exception as e:
            logging.error(f"清理资源失败: {str(e)}")

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
            self.update_icon('green')
            threading.Thread(target=self.guardian_thread, daemon=True).start()
            logging.info("守护模式已启动")
            return True
        
        return False

    def stop_guardian(self):
        """
        停止守护
        """
        logging.info("开始执行停止守护")
        if self.guardian.stop_guardian(manual=True):
            logging.info("守护已停止，更新图标")
            self.update_icon('gray')
            return True
        logging.info("停止守护失败")
        return False

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
        
        warning_shown = False  # 添加标志位，避免重复显示警告
        
        while True:
            try:
                # 只在非守护模式下检测空闲时间
                if not self.guardian.is_guarding:
                    warning_shown = False  # 重置标志位
                    # 获取并显示空闲时间
                    idle_time = self.guardian.get_idle_duration()
                    print(f"\r当前空闲时间：{idle_time:.1f}秒，设定阈值：{self.guardian.idle_time_threshold}秒", end='', flush=True)
                    
                    # 检查是否需要进入守护模式
                    if idle_time > self.guardian.idle_time_threshold:
                        print(f"\n系统已空闲 {idle_time:.1f} 秒，进入守护模式！")
                        print("=" * 50)
                        self.guardian.is_guarding = True
                        # 更新图标为绿色
                        self.update_icon('green')
                
                # 在守护模式下只检查微信窗口
                elif self.guardian.is_wechat_active() and not warning_shown:
                    # 先锁定微信
                    self.guardian.lock_wechat()
                    
                    # 立即显示警告窗口
                    warning = tk.Toplevel()
                    warning.title("警告")
                    warning.geometry("1125x808")
                    warning.resizable(False, False)
                    
                    # 使用 Segoe UI Emoji 字体显示彩色表情
                    label = tk.Label(
                        warning, 
                        text="😈 喂～你坏蛋 😈\n不要看我微信", 
                        font=("Segoe UI Emoji", 48),
                        justify=tk.CENTER
                    )
                    label.pack(expand=True)
                    
                    # 创建一个大号按钮样式
                    style = ttk.Style()
                    style.configure(
                        "Big.TButton",
                        padding=(20, 10),
                        font=("微软雅黑", 16)
                    )
                    
                    # 添加放大的确定按钮
                    ttk.Button(
                        warning, 
                        text="好的，我错了", 
                        command=warning.destroy,
                        style="Big.TButton"
                    ).pack(pady=30)
                    
                    warning.transient()
                    warning.grab_set()
                    warning.focus_set()
                    
                    # 更新状态
                    self.guardian.is_guarding = False
                    self.update_icon('gray')
                    warning_shown = True
                
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

    def start_guardian_thread(self):
        """
        启动守护线程
        """
        threading.Thread(target=self.guardian_thread, daemon=True).start()

    def update_icon(self, color):
        """
        更新系统托盘图标
        """
        try:
            icon = self.green_icon if color == 'green' else self.gray_icon
            temp_icon_path = os.path.join(os.path.dirname(__file__), f'temp_{color}_icon.ico')
            icon.save(temp_icon_path, format='ICO', sizes=[(16, 16)])
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
        except Exception as e:
            logging.error(f"更新图标失败: {str(e)}")

def main():
    try:
        app = WeChatGuardianApp()
        app.run()
    except Exception as e:
        logging.critical(f"程序启动失败: {e}")
        print(f"程序启动失败: {e}")

if __name__ == '__main__':
    main()
