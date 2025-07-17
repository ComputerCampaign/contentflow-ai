#!/bin/bash

# 验证 JavaScript 脚本注入示例脚本

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1

# 颜色定义
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== JavaScript 脚本注入验证工具示例 =====${NC}\n"

# 1. 使用本地测试页面验证（有头模式）
echo -e "${GREEN}1. 使用本地测试页面验证（有头模式）${NC}"
echo "这将打开一个浏览器窗口，显示测试结果"
echo "命令: python verify_js_injection.py"
echo -e "${YELLOW}按回车键继续...${NC}"
read -r
python verify_js_injection.py
echo 

# 2. 使用本地测试页面验证（无头模式）
echo -e "${GREEN}2. 使用本地测试页面验证（无头模式）${NC}"
echo "命令: python verify_js_injection.py --headless"
echo -e "${YELLOW}按回车键继续...${NC}"
read -r
python verify_js_injection.py --headless
echo 

# 3. 验证特定URL（有头模式）
echo -e "${GREEN}3. 验证特定URL（有头模式）${NC}"
echo "命令: python verify_js_injection.py --url https://bot.sannysoft.com/"
echo "注意: bot.sannysoft.com 是一个专门用于测试爬虫检测的网站"
echo -e "${YELLOW}按回车键继续...${NC}"
read -r
python verify_js_injection.py --url https://bot.sannysoft.com/
echo 

# 4. 验证特定URL（无头模式）
echo -e "${GREEN}4. 验证特定URL（无头模式）${NC}"
echo "命令: python verify_js_injection.py --headless --url https://bot.sannysoft.com/"
echo -e "${YELLOW}按回车键继续...${NC}"
read -r
python verify_js_injection.py --headless --url https://bot.sannysoft.com/
echo 

echo -e "${GREEN}===== 示例运行完成 =====${NC}"
echo -e "${YELLOW}提示:${NC}"
echo "1. 如果测试结果显示脚本注入失败，请检查以下几点:"
echo "   - 确保 stealth.min.js 文件存在于 config/scripts/ 目录下"
echo "   - 检查 SeleniumRenderer 类中的脚本注入代码是否正确"
echo "   - 尝试更新 stealth.min.js 到最新版本"
echo 

echo "2. 对于特定网站的验证，可以使用以下命令:"
echo "   python verify_js_injection.py --url YOUR_TARGET_URL"
echo 

echo "3. 查看测试结果和截图:"
echo "   测试结果和截图保存在 output/temp/ 目录下"
echo