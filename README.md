# 微信守护程序

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

## 安装与构建

### 直接下载

你可以在 [Releases](https://github.com/flyhunterl/wechatguard/releases) 页面下载最新的可执行文件。

### 从源代码构建

#### 环境准备

1. 确保已安装 Python 3.9 或更高版本
2. 克隆仓库
```bash
git clone https://github.com/flyhunterl/wechatguard.git
cd wechatguard
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 运行程序
```bash
python src/main.py
```

#### 打包可执行文件
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=src/icon/app_icon.ico --name="WeChatGuard" src/main.py
```

## 开发状态

![Build Status](https://github.com/flyhunterl/wechatguard/workflows/Build%20WeChatGuard%20Executable/badge.svg)

## 注意事项

- 请始终以管理员权限运行
- 尊重他人隐私
- 仅在合法和有道德的情况下使用

## 许可证

MIT License

## 项目链接
- GitHub仓库: [https://github.com/flyhunterl/wechatguard](https://github.com/flyhunterl/wechatguard)
- 作者博客: [https://llingfei.com](https://llingfei.com)

## 贡献

欢迎提交 Issues 和 Pull Requests！
