# JavaScript 脚本注入验证指南

## 概述

在使用 Selenium 进行网页爬取时，为了绕过反爬虫检测，我们通常会注入一些 JavaScript 脚本（如 stealth.min.js）来隐藏 Selenium WebDriver 的特征。然而，有时脚本可能没有正确注入，导致爬虫被网站检测并阻止。本指南将帮助你验证 JavaScript 脚本是否正确注入，并提供常见问题的解决方案。

## 验证工具

我们提供了以下工具来验证 JavaScript 脚本注入：

1. **验证脚本**: `verify_js_injection.py`
2. **测试类**: `tests/test_js_injection.py`
3. **验证器类**: `crawler_utils/js_injection_validator.py`
4. **示例脚本**: `examples/verify_js_injection_example.sh`

## 使用方法

### 1. 使用验证脚本

最简单的方法是直接运行验证脚本：

```bash
# 使用本地测试页面验证（有头模式，会打开浏览器窗口）
python verify_js_injection.py

# 使用本地测试页面验证（无头模式）
python verify_js_injection.py --headless

# 验证特定URL（有头模式）
python verify_js_injection.py --url https://example.com

# 验证特定URL（无头模式）
python verify_js_injection.py --headless --url https://example.com
```

### 2. 运行示例脚本

我们提供了一个示例脚本，演示了各种验证方法：

```bash
bash examples/verify_js_injection_example.sh
```

### 3. 运行测试

你也可以运行测试类来验证脚本注入：

```bash
python -m unittest tests/test_js_injection.py
```

### 4. 在代码中使用验证器

你可以在自己的代码中使用验证器类：

```python
from crawler_utils.selenium_renderer import SeleniumRenderer
from crawler_utils.js_injection_validator import JSInjectionValidator

# 初始化 SeleniumRenderer
renderer = SeleniumRenderer(headless=False)

# 初始化验证器
validator = JSInjectionValidator(renderer)

# 验证脚本注入
is_injected, details = validator.validate_injection()
print(f"JavaScript 脚本注入状态: {'成功' if is_injected else '失败'}")
print(details)

# 或者使用测试页面
success, result = validator.create_test_page()
print(result)

# 关闭 WebDriver
renderer.close()
```

## 验证结果解读

验证工具会检查以下几个关键属性，以判断脚本是否正确注入：

1. **navigator.webdriver**: 应该是 `undefined` 或 `false`（正常浏览器中不存在此属性，或值为 false）
2. **window.chrome**: 应该存在（正常浏览器中存在此对象）
3. **navigator.plugins.length**: 应该大于 0（正常浏览器中有插件）
4. **navigator.languages**: 应该存在且非空（正常浏览器中有语言设置）

如果以上条件都满足，则认为脚本注入成功。特别注意，对于 **navigator.webdriver** 属性，在不同的浏览器和 stealth.js 版本中，可能会返回 `undefined` 或 `false`，两者都表示脚本注入成功。

## 常见问题及解决方案

### 1. 脚本文件不存在或路径错误

**症状**: 日志中显示 "注入反爬虫检测绕过脚本失败: [Errno 2] No such file or directory: '...'"

**解决方案**:
- 确保 `stealth.min.js` 文件存在于 `config/scripts/` 目录下
- 检查 `SeleniumRenderer` 类中的文件路径是否正确

### 2. 脚本注入成功但仍被检测

**症状**: 验证工具显示脚本注入成功，但网站仍然检测到爬虫

**解决方案**:
- 尝试更新 `stealth.min.js` 到最新版本
- 检查网站是否使用了其他方法检测爬虫（如指纹识别、行为分析等）
- 尝试添加更多的反检测措施，如修改 User-Agent、添加更多浏览器特征等

### 3. 页面加载超时

**症状**: 验证过程中出现 "页面加载超时" 错误

**解决方案**:
- 增加 `page_load_wait` 参数的值
- 检查网络连接是否稳定
- 如果使用代理，检查代理是否正常工作

### 4. WebDriver 初始化失败

**症状**: 无法创建 WebDriver 实例

**解决方案**:
- 确保已安装正确版本的 Chrome 和 ChromeDriver
- 检查 Chrome 和 ChromeDriver 版本是否匹配
- 尝试使用 `webdriver_manager` 自动下载匹配的 ChromeDriver

## 高级技巧

### 1. 自定义 stealth.js

如果默认的 `stealth.min.js` 不能满足需求，你可以自定义脚本或使用其他反检测脚本：

```python
# 在 SeleniumRenderer 类中修改
def _create_stealth_driver(self):
    # ...
    # 注入自定义脚本
    custom_js = """
    // 自定义的反检测 JavaScript 代码
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    // 更多代码...
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": custom_js
    })
    # ...
```

### 2. 使用 CDP 命令检查注入状态

你可以使用 Chrome DevTools Protocol (CDP) 命令来检查脚本是否正确注入：

```python
def check_injection_with_cdp(driver):
    # 获取所有已注入的脚本
    scripts = driver.execute_cdp_cmd("Page.getScriptsToEvaluateOnNewDocument", {})
    print("已注入的脚本:", scripts)
    return scripts
```

### 3. 在特定网站上测试

有些网站专门用于测试爬虫检测，你可以在这些网站上验证你的反检测措施：

- [https://bot.sannysoft.com/](https://bot.sannysoft.com/)
- [https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html](https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html)

## 结论

正确验证 JavaScript 脚本注入是确保爬虫能够绕过反爬虫检测的重要步骤。使用本指南提供的工具和方法，你可以轻松验证脚本是否正确注入，并解决常见问题。

如果你遇到其他问题或需要更多帮助，请查看项目文档或提交 Issue。