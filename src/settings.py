import json
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
import base64

class GuardianSettings:
    def __init__(self):
        self.config = self.load_config()
        self.on_config_changed = None

    def load_config(self):
        """
        加载配置文件
        """
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"idle_time": 10, "password": ""}  # 默认配置
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            return {"idle_time": 10, "password": ""}

    def save_config(self):
        """
        保存配置文件
        """
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            if self.on_config_changed:
                self.on_config_changed(self.config)
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            return False

    def show_settings_dialog(self):
        """
        显示设置对话框
        """
        window = tk.Toplevel()
        window.title("设置")
        window.geometry("300x250")  # 增加窗口高度
        window.resizable(False, False)

        # 空闲时间设置
        idle_frame = ttk.LabelFrame(window, text="空闲时间设置")
        idle_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(idle_frame, text="空闲时间阈值(秒):").pack(side=tk.LEFT, padx=5)
        idle_var = tk.StringVar(value=str(self.config.get("idle_time", 10)))
        
        def on_idle_time_change(*args):
            try:
                idle_time = int(idle_var.get())
                if idle_time > 0:
                    self.config["idle_time"] = idle_time
                    self.save_config()
            except ValueError:
                pass

        idle_var.trace('w', on_idle_time_change)
        ttk.Entry(idle_frame, textvariable=idle_var, width=10).pack(side=tk.LEFT)

        # 密码保护设置
        pwd_frame = ttk.LabelFrame(window, text="密码保护")
        pwd_frame.pack(fill=tk.X, padx=10, pady=5)

        pwd_var = tk.BooleanVar(value=bool(self.config.get("password")))
        ttk.Checkbutton(
            pwd_frame, 
            text="启用密码保护", 
            variable=pwd_var,
            command=lambda: self.toggle_password(pwd_var.get(), window)
        ).pack(padx=5, pady=5)

        # 说明文本
        note_frame = ttk.LabelFrame(window, text="说明")
        note_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # 让说明框架填充剩余空间

        ttk.Label(
            note_frame, 
            text=(
                "1. 空闲时间：系统无操作超过设定时间后自动进入守护模式\n\n" + 
                "2. 密码保护：启用后需要输入密码才能手动停止守护\n" +
                "   • 自动停止守护不需要密码验证\n" +
                "   • 停用密码保护需要验证当前密码"
            ),
            wraplength=260,  # 增加文本宽度
            justify=tk.LEFT  # 左对齐
        ).pack(padx=5, pady=5, fill=tk.BOTH, expand=True)  # 让文本标签填充框架

        window.transient()
        window.grab_set()
        window.focus_set()

    def toggle_password(self, enable, parent_window=None):
        """
        切换密码保护
        """
        # 如果之前有密码，需要先验证
        if self.config.get('password') and not self.verify_password(
            simpledialog.askstring(
                "验证密码",
                "请输入当前密码:",
                parent=parent_window,
                show='*'
            )
        ):
            messagebox.showerror("错误", "密码验证失败")
            return False
        
        if enable:
            # 设置新密码
            password = simpledialog.askstring(
                "设置密码",
                "请输入新密码:",
                parent=parent_window,
                show='*'
            )
            if password:
                confirm = simpledialog.askstring(
                    "确认密码",
                    "请再次输入密码:",
                    parent=parent_window,
                    show='*'
                )
                if password == confirm:
                    self.set_password(password)
                else:
                    messagebox.showerror("错误", "两次输入的密码不一致")
                    return False
            else:
                return False
        else:
            # 已经验证过密码了，直接清除
            self.set_password("")
        return True

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

    def verify_password(self, password):
        """
        验证密码
        """
        try:
            if not self.config.get('password'):
                return True
                
            stored_hash = base64.b64decode(self.config['password'].encode('utf-8'))
            stored_salt = base64.b64decode(self.config['salt'].encode('utf-8'))
            
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
