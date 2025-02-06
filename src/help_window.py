import tkinter as tk
from tkinter import ttk
import webbrowser

class HelpWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("帮助")
        self.window.geometry("400x450")
        self.window.resizable(False, False)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建不同的分区
        sections = [
            ("主要功能", [
                "• 自动监控系统空闲时间",
                "• 达到设定阈值后自动进入守护模式",
                "• 在守护模式下自动锁定微信窗口并显示警告",
                "• 系统托盘显示程序状态"
            ]),
            ("使用说明", [
                "1. 程序启动后会在系统托盘显示图标",
                "   • 灰色：正在监控空闲时间",
                "   • 绿色：已进入守护模式",
                "2. 右键托盘图标可以：",
                "   • 开始/停止守护",
                "   • 查看设置",
                "   • 查看帮助",
                "   • 退出程序"
            ]),
            ("设置说明", [
                "• 空闲时间阈值：设置多少秒无操作后进入守护模式",
                "• 密码保护：启用后需要输入密码才能手动停止守护",
                "  - 自动停止守护不需要密码验证",
                "  - 停用密码保护需要验证当前密码"
            ]),
            ("注意事项", [
                "• 需要管理员权限运行",
                "• 仅支持 Windows 系统",
                "• 建议将程序添加到开机启动项"
            ])
        ]
        
        # 创建文本框
        text = tk.Text(main_frame, wrap=tk.WORD, width=45, height=20)
        text.pack(fill=tk.BOTH, expand=True)
        
        # 插入标题
        text.tag_configure("title", font=("微软雅黑", 12, "bold"))
        text.tag_configure("content", font=("微软雅黑", 10))
        
        text.insert(tk.END, "WeChat Guardian (微信守护程序)\n\n", "title")
        
        # 插入各个部分
        for section_title, content in sections:
            text.insert(tk.END, f"{section_title}：\n", "title")
            for line in content:
                text.insert(tk.END, f"{line}\n", "content")
            text.insert(tk.END, "\n")
        
        text.config(state=tk.DISABLED)
        
        # 添加按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        # 添加项目主页按钮
        ttk.Button(
            button_frame, 
            text="访问项目主页", 
            command=lambda: webbrowser.open("https://github.com/flyhunterl/wechatguard")
        ).pack(side=tk.LEFT, padx=5)
        
        # 添加作者博客按钮
        ttk.Button(
            button_frame, 
            text="访问作者博客", 
            command=lambda: webbrowser.open("https://llingfei.com")
        ).pack(side=tk.LEFT, padx=5)
        
        # 添加关闭按钮
        ttk.Button(
            button_frame, 
            text="关闭", 
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # 设置模态窗口
        self.window.transient()
        self.window.grab_set()
        self.window.focus_set()

    @staticmethod
    def show_help():
        HelpWindow()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    HelpWindow.show_help()
    root.mainloop()
