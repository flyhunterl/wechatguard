import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import hashlib

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
            "password_enabled": False,  # 默认不启用密码保护
            "password": "",
            "idle_time": 60
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 合并默认配置和保存的配置，确保新的默认值生效
                    merged_config = {**default_config, **saved_config}
                    
                    # 如果没有密码，强制禁用密码保护
                    if not merged_config.get("password"):
                        merged_config["password_enabled"] = False
                    
                    return merged_config
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

    def hash_password(self, password):
        """
        对密码进行哈希处理
        """
        return hashlib.sha256(password.encode()).hexdigest() if password else ""

    def verify_password(self, input_password, stored_password):
        """
        验证密码
        """
        return self.hash_password(input_password) == stored_password

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

        # 记录原始密码和启用状态
        original_password = self.config.get("password", "")
        original_password_enabled = self.config.get("password_enabled", False) and bool(original_password)

        password_var = tk.BooleanVar(value=original_password_enabled)
        password_check = ttk.Checkbutton(
            password_frame, 
            text="启用密码（需重启程序）", 
            variable=password_var
        )
        password_check.pack(anchor="w")

        password_label = ttk.Label(password_frame, text="密码:")
        password_label.pack(anchor="w")

        password_entry = ttk.Entry(password_frame, show="*")
        password_entry.pack(anchor="w", fill="x", padx=10)

        def save_settings():
            # 获取密码状态和密码
            is_password_enabled = password_var.get()
            new_password = password_entry.get()

            # 如果没有输入新密码，但要求启用密码，则保持原密码状态
            if is_password_enabled and not new_password:
                if not original_password:
                    messagebox.showerror("错误", "请输入密码")
                    return

            # 处理密码逻辑
            if new_password:
                # 如果输入了新密码，哈希并保存
                hashed_password = self.hash_password(new_password)
                self.config["password"] = hashed_password
                self.config["password_enabled"] = True
            else:
                # 没有新密码，根据复选框状态决定
                self.config["password_enabled"] = False
                self.config["password"] = ""

            # 保存配置
            self.save_config()
            window.destroy()

        save_button = ttk.Button(window, text="保存", command=save_settings)
        save_button.pack(pady=10)

        # 空闲时间设置
        idle_frame = ttk.LabelFrame(window, text="空闲时间")
        idle_frame.pack(padx=10, pady=10, fill="x")

        idle_label = ttk.Label(idle_frame, text="空闲时间阈值（秒）:")
        idle_label.pack(anchor="w")

        idle_var = tk.IntVar(value=self.config.get("idle_time", 60))
        idle_entry = ttk.Entry(idle_frame, textvariable=idle_var)
        idle_entry.pack(anchor="w", fill="x", padx=10)

        def save_idle_time():
            try:
                idle_time = int(idle_var.get())
                if idle_time > 0:
                    self.config["idle_time"] = idle_time
                    self.save_config()
                else:
                    messagebox.showerror("错误", "空闲时间必须为正整数")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")

        idle_save_button = ttk.Button(idle_frame, text="保存", command=save_idle_time)
        idle_save_button.pack(pady=5)

        window.mainloop()

# 示例使用
if __name__ == '__main__':
    settings = GuardianSettings()
    settings.open_settings_window()
