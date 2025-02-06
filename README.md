# WeChat Guardian (微信守护程序)

一个自动监控系统空闲时间并在需要时锁定微信的工具。

## 主要功能

- 自动监控系统空闲时间
- 达到设定阈值后自动进入守护模式
- 在守护模式下自动锁定微信窗口并显示警告
- 系统托盘显示程序状态
- 可自定义空闲时间阈值
- 支持密码保护

## 使用说明

1. 以管理员权限运行程序
2. 程序启动后会在系统托盘显示图标：
   - 灰色图标：正在监控空闲时间
   - 绿色图标：已进入守护模式
3. 右键托盘图标可以：
   - 开始/停止守护
   - 查看设置
   - 查看帮助
   - 退出程序

## 设置说明

- 空闲时间阈值：设置多少秒无操作后进入守护模式
- 密码保护：启用后需要输入密码才能手动停止守护
  - 自动停止守护不需要密码验证
  - 停用密码保护需要验证当前密码

## 注意事项

- 需要管理员权限运行
- 仅支持 Windows 系统
- 建议将程序添加到开机启动项

## 版本历史

### v0.3.2
- 优化设置窗口说明文本显示
- 改进帮助窗口布局和内容
- 添加作者博客链接
- 代码清理和优化

### v0.3.0
- 改进密码保护机制
- 优化警告窗口显示
- 改进空闲时间检测逻辑
- 修复重复警告窗口的问题

### v0.2.7
- 添加自动更新检查功能
- 修复依赖和导入问题

### v0.1.5
- 初始版本发布

## 许可证

MIT License

## 项目链接
- GitHub仓库: [https://github.com/flyhunterl/wechatguard](https://github.com/flyhunterl/wechatguard)
- 作者博客: [https://llingfei.com](https://llingfei.com)

## 贡献

欢迎提交 Issues 和 Pull Requests！
