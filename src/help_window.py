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

## 功能特点
- 🛡️ 微信窗口守护
- 🕒 系统空闲时间检测
- 🔐 密码保护设置
- 🖥️ 系统托盘图标管理

## 环境要求
- Windows 10/11
- 管理员权限

## 使用方法

### 启动程序
- 以管理员权限运行
- 双击图标进入守护模式

### 系统托盘菜单
- 开始守护：进入守护模式
- 停止守护：退出守护模式
- 设置：配置守护密码(可选)和空闲时间
- 帮助：查看使用说明
- 退出：关闭程序

## 注意事项
- 请始终以管理员权限运行
- 尊重他人隐私
- 仅在合法和有道德的情况下使用

## 项目链接
- GitHub仓库: https://github.com/flyhunterl/wechatguard
- 作者博客: https://llingfei.com

## 许可证
MIT License

## 贡献
欢迎提交 Issues 和 Pull Requests！
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
