import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import hashlib
import logging
import base64

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
        self.on_config_changed = None

    def load_config(self):
        """
        加载配置文件
        :return: 配置字典
        """
        default_config = {
            "password_enabled": False,  # 默认不启用密码保护
            "password": "",
            "idle_time": 10
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
            
            # 通知其他组件配置已更新
            if self.on_config_changed:
                self.on_config_changed(self.config)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存配置: {e}")

    def hash_password(self, password):
        """
        对密码进行哈希处理
        """
        return hashlib.sha256(password.encode()).hexdigest() if password else ""

    def verify_password(self, password):
        """
        验证密码
        """
        try:
            if not self.config.get('password'):
                return True
                
            stored_salt = base64.b64decode(self.config['salt'].encode('utf-8'))
            stored_hash = base64.b64decode(self.config['password'].encode('utf-8'))
            
            # 使用相同的盐值计算哈希
            input_hash = self._hash_password(password, stored_salt)
            
            # 使用安全的比较方法
            return self._secure_compare(stored_hash, input_hash)
        except Exception as e:
            logging.error(f"密码验证失败: {str(e)}")
            return False
            
    def _hash_password(self, password, salt):
        """
        使用 PBKDF2 和 SHA256 哈希密码
        """
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # 迭代次数
        )
        
    def _secure_compare(self, a, b):
        """
        安全的字符串比较，避免时序攻击
        """
        return len(a) == len(b) and all(
            x == y for x, y in zip(a, b)
        )

    def open_settings_window(self):
        """
        打开设置窗口
        """
        window = tk.Tk()
        window.title("微信守护程序 - 设置")
        window.geometry("400x400")  # 增加窗口高度

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
        idle_frame = ttk.LabelFrame(window, text="空闲时间设置")
        idle_frame.pack(padx=10, pady=10, fill="x")

        idle_var = tk.IntVar(value=self.config.get("idle_time", 10))
        
        def update_idle_label(value):
            idle_label.config(text=f"空闲时间阈值: {int(float(value))} 秒")
        
        idle_label = ttk.Label(idle_frame, text=f"空闲时间阈值: {idle_var.get()} 秒")
        idle_label.pack(anchor="w", padx=10, pady=5)

        idle_scale = ttk.Scale(
            idle_frame,
            from_=5,
            to=300,
            orient="horizontal",
            variable=idle_var,
            command=update_idle_label
        )
        idle_scale.pack(fill="x", padx=10, pady=5)

        def save_idle_time():
            idle_time = int(idle_var.get())
            self.config["idle_time"] = idle_time
            self.save_config()
            messagebox.showinfo("成功", f"空闲时间已设置为 {idle_time} 秒")

        idle_save_button = ttk.Button(idle_frame, text="保存空闲时间设置", command=save_idle_time)
        idle_save_button.pack(pady=10)  # 增加按钮的上下边距

        window.mainloop()

    def set_password(self, password):
        """
        设置密码
        """
        try:
            if not password:  # 如果密码为空，则禁用密码保护
                self.config['password'] = ''
                self.config['salt'] = ''
            else:
                # 生成随机盐值
                salt = os.urandom(16)
                # 使用盐值和密码生成哈希
                hashed = self._hash_password(password, salt)
                
                self.config['salt'] = base64.b64encode(salt).decode('utf-8')
                self.config['password'] = base64.b64encode(hashed).decode('utf-8')
            
            self.save_config()
            return True
        except Exception as e:
            logging.error(f"设置密码失败: {str(e)}")
            return False

# 示例使用
if __name__ == '__main__':
    settings = GuardianSettings()
    settings.open_settings_window()
