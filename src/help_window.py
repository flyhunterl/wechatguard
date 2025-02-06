import tkinter as tk
from tkinter import ttk

class HelpWindow:
    @staticmethod
    def show_help():
        """
        显示帮助窗口
        """
        window = tk.Tk()
        window.title("微信守护程序 - 帮助")
        window.geometry("500x600")

        help_text = """
微信守护程序 使用说明

1. 程序图标说明
   - 灰色图标：非守护模式
   - 绿色图标：守护模式已开启

2. 系统托盘菜单
   - 开始守护：进入守护模式，图标变为绿色
   - 停止守护：退出守护模式，图标恢复灰色
   - 设置：打开设置界面，可配置密码和空闲时间
   - 帮助：显示本帮助窗口
   - 退出：关闭程序

3. 守护模式触发条件
   - 微信窗口被激活
   - 系统空闲时间超过设定阈值

4. 触发守护时
   - 自动使用 Ctrl+L 锁定微信
   - 弹出有趣的警告消息
   - 自动停止守护模式

5. 密码保护
   - 可在设置中启用/禁用
   - 停止守护模式时可能需要输入密码

注意事项：
- 请以管理员权限运行程序
- 程序仅在检测到微信窗口时生效
- 尊重他人隐私，谨慎使用
"""

        help_label = ttk.Label(window, text="微信守护程序使用说明", font=("微软雅黑", 16, "bold"))
        help_label.pack(pady=10)

        text_widget = tk.Text(window, wrap=tk.WORD, font=("微软雅黑", 10))
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # 设为只读

        scrollbar = ttk.Scrollbar(window, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        close_button = ttk.Button(window, text="关闭", command=window.destroy)
        close_button.pack(pady=10)

        window.mainloop()

# 示例使用
if __name__ == '__main__':
    HelpWindow.show_help()
