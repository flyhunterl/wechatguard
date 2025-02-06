import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class GuardianSettings:
    def __init__(self, config_path=None):
        """
        守护程序设置管理
        :param config_path: 配置文件路径
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """
        加载配置文件
        :return: 配置字典
        """
        default_config = {
            "password_enabled": False,
            "password": "",
            "idle_time": 60
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    return {**default_config, **saved_config}
            except Exception:
                return default_config
        
        return default_config

    def save_config(self):
        """
        保存配置文件
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存配置: {e}")

    def open_settings_window(self):
        """
        打开设置窗口
        """
        window = tk.Tk()
        window.title("微信守护程序 - 设置")
        window.geometry("400x300")

        # 密码设置
        password_frame = ttk.LabelFrame(window, text="密码保护")
        password_frame.pack(padx=10, pady=10, fill="x")

        password_var = tk.BooleanVar(value=self.config["password_enabled"])
        password_check = ttk.Checkbutton(
            password_frame, 
            text="启用密码", 
            variable=password_var, 
            command=lambda: self.config.update({"password_enabled": password_var.get()})
        )
        password_check.pack(anchor="w")

        password_label = ttk.Label(password_frame, text="密码:")
        password_label.pack(anchor="w")
        password_entry = ttk.Entry(password_frame, show="*")
        password_entry.pack(fill="x", padx=10)

        # 空闲时间设置
        idle_frame = ttk.LabelFrame(window, text="空闲检测")
        idle_frame.pack(padx=10, pady=10, fill="x")

        idle_label = ttk.Label(idle_frame, text="空闲时间阈值（秒）:")
        idle_label.pack(anchor="w")

        idle_var = tk.IntVar(value=self.config["idle_time"])
        idle_scale = ttk.Scale(
            idle_frame, 
            from_=10, to=300, 
            variable=idle_var, 
            orient=tk.HORIZONTAL
        )
        idle_scale.pack(fill="x", padx=10)

        idle_value_label = ttk.Label(idle_frame, textvariable=idle_var)
        idle_value_label.pack()

        def save_settings():
            self.config.update({
                "password": password_entry.get(),
                "idle_time": idle_var.get()
            })
            self.save_config()
            window.destroy()

        save_button = ttk.Button(window, text="保存设置", command=save_settings)
        save_button.pack(pady=10)

        window.mainloop()

# 示例使用
if __name__ == '__main__':
    settings = GuardianSettings()
    settings.open_settings_window()
