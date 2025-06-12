# ClockInSystem-Bot

这是一个使用 Playwright 自动化框架编写的 Python 脚本，用ybot对ClockInSystem进行签到打卡操作。

## 功能特点

- 支持多浏览器并发操作
- 自动化表单填写（钱包地址、私钥等）
- 自动设置 Gas 费率
- 等待特定区块高度
- 支持用户手动中断操作

## 环境要求

- Python 3.7+
- Playwright
- aiohttp

## 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

## 配置文件

在项目根目录创建 `sign-wallet.txt` 文件，每行包含一个钱包信息，格式如下：
```
钱包地址----私钥
```

## 使用方法

1. 安装依赖
2. 配置钱包文件
3. 运行脚本：
```bash
python main.py
```

如需确认提交，则需要将main.py里面的代码注释去掉

![1749700065864](https://github.com/user-attachments/assets/e83c0449-66ef-453e-96ed-567399671b09)


## 主要功能

1. **区块高度检查**
   - 自动检查当前区块高度
   - 等待直到达到目标区块高度

2. **浏览器自动化**
   - 自动打开多个浏览器实例
   - 自动填写表单数据
   - 自动设置 Gas 费率

3. **用户控制**
   - 支持用户手动确认和中断操作
   - 提供详细的操作日志

## 注意事项

- 请确保网络连接稳定
- 请妥善保管私钥信息
- 建议在运行前先测试小规模操作

## 许可证

MIT License

## 免责声明

本项目仅供学习和研究使用，使用本项目产生的任何后果由使用者自行承担。 
