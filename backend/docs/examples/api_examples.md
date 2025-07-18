# API使用示例

本文档提供了使用爬虫系统API的完整示例，包括认证、爬虫任务创建、XPath规则管理等操作。

## 认证流程示例

### 用户注册与登录

```python
import requests

# API基础URL
base_url = 'http://localhost:8000/api'

# 注册新用户
def register_user(username, email, password):
    response = requests.post(
        f'{base_url}/auth/register',
        json={
            'username': username,
            'email': email,
            'password': password
        }
    )
    return response.json()

# 用户登录
def login_user(username, password):
    response = requests.post(
        f'{base_url}/auth/login',
        json={
            'username': username,
            'password': password
        }
    )
    return response.json()

# 示例使用
user_data = register_user('testuser', 'test@example.com', 'securepassword')
print(f"用户注册结果: {user_data}")

login_data = login_user('testuser', 'securepassword')
token = login_data.get('access_token')
print(f"获取到的访问令牌: {token}")
```

## 爬虫任务示例

### 创建爬虫任务并获取结果

```python
import requests
import time

# 设置认证头
headers = {'Authorization': f'Bearer {token}'}

# 创建爬虫任务
def create_crawler_task(url, use_xpath=False, xpath_rule_id=None, blog_template=None):
    payload = {
        'url': url,
        'use_selenium': True,
        'use_xpath': use_xpath
    }
    
    if use_xpath and xpath_rule_id:
        payload['xpath_rule_id'] = xpath_rule_id
        payload['is_user_rule'] = False  # 使用系统规则
    
    if blog_template:
        payload['blog_template'] = blog_template
    
    response = requests.post(
        f'{base_url}/crawler/tasks',
        headers=headers,
        json=payload
    )
    return response.json()

# 获取任务状态
def get_task_status(task_id):
    response = requests.get(
        f'{base_url}/crawler/tasks/{task_id}',
        headers=headers
    )
    return response.json()

# 示例使用
task_data = create_crawler_task(
    'https://example.com/article',
    use_xpath=True,
    xpath_rule_id='general_article',
    blog_template='default'
)

task_id = task_data.get('task_id')
print(f"任务创建成功，ID: {task_id}")

# 等待任务完成并获取结果
max_retries = 10
for i in range(max_retries):
    task_info = get_task_status(task_id)
    status = task_info.get('status')
    print(f"任务状态: {status}")
    
    if status == 'success':
        print("任务完成！输出文件:")
        for file in task_info.get('output_files', []):
            print(f"- {file['name']} ({file['size']} bytes)")
        break
    elif status == 'failed':
        print(f"任务失败")
        break
    
    if i < max_retries - 1:
        print("等待任务完成...")
        time.sleep(5)  # 等待5秒后再次检查
```

## XPath规则管理示例

### 创建和使用自定义XPath规则

```python
import requests

# 设置认证头
headers = {'Authorization': f'Bearer {token}'}

# 创建XPath规则
def create_xpath_rule(name, domain, xpath, description=None):
    payload = {
        'name': name,
        'domain': domain,
        'xpath': xpath
    }
    
    if description:
        payload['description'] = description
    
    response = requests.post(
        f'{base_url}/xpath/rules',
        headers=headers,
        json=payload
    )
    return response.json()

# 获取用户规则列表
def get_user_rules():
    response = requests.get(
        f'{base_url}/xpath/rules',
        headers=headers
    )
    return response.json()

# 示例使用
rule_data = create_xpath_rule(
    '技术博客规则',
    'tech.example.com',
    "//div[@class='article-content']",
    '提取技术博客的文章内容'
)

rule_id = rule_data.get('id')
print(f"规则创建成功，ID: {rule_id}")

# 使用自定义规则创建爬虫任务
task_data = create_crawler_task(
    'https://tech.example.com/article',
    use_xpath=True,
    xpath_rule_id=rule_id,
    blog_template='tech_blog'
)

task_id = task_data.get('task_id')
print(f"使用自定义规则创建任务成功，ID: {task_id}")
```

## 完整工作流示例

以下是一个完整的工作流示例，包括用户注册、登录、创建XPath规则、提交爬虫任务和获取结果：

```python
import requests
import time
import json

# API基础URL
base_url = 'http://localhost:8000/api'

# 1. 用户注册
register_response = requests.post(
    f'{base_url}/auth/register',
    json={
        'username': 'demo_user',
        'email': 'demo@example.com',
        'password': 'demo_password'
    }
)
print("1. 用户注册结果:")
print(json.dumps(register_response.json(), indent=2))

# 2. 用户登录
login_response = requests.post(
    f'{base_url}/auth/login',
    json={
        'username': 'demo_user',
        'password': 'demo_password'
    }
)
login_data = login_response.json()
token = login_data.get('access_token')
print("\n2. 用户登录结果:")
print(json.dumps(login_data, indent=2))

# 设置认证头
headers = {'Authorization': f'Bearer {token}'}

# 3. 获取用户信息
user_info_response = requests.get(
    f'{base_url}/auth/me',
    headers=headers
)
print("\n3. 用户信息:")
print(json.dumps(user_info_response.json(), indent=2))

# 4. 获取系统预设XPath规则
system_rules_response = requests.get(
    f'{base_url}/xpath/system-rules',
    headers=headers
)
system_rules = system_rules_response.json().get('rules', [])
print("\n4. 系统预设XPath规则:")
print(json.dumps(system_rules, indent=2))

# 5. 创建自定义XPath规则
custom_rule_response = requests.post(
    f'{base_url}/xpath/rules',
    headers=headers,
    json={
        'name': '自定义新闻规则',
        'domain': 'news.example.com',
        'xpath': "//div[@class='news-content']",
        'description': '提取新闻网站的文章内容'
    }
)
custom_rule = custom_rule_response.json()
print("\n5. 创建自定义XPath规则:")
print(json.dumps(custom_rule, indent=2))

# 6. 获取可用博客模板
templates_response = requests.get(
    f'{base_url}/crawler/templates',
    headers=headers
)
templates = templates_response.json().get('templates', [])
print("\n6. 可用博客模板:")
print(json.dumps(templates, indent=2))

# 7. 创建爬虫任务
task_response = requests.post(
    f'{base_url}/crawler/tasks',
    headers=headers,
    json={
        'url': 'https://news.example.com/article',
        'task_name': '示例新闻爬取',
        'use_selenium': True,
        'use_xpath': True,
        'xpath_rule_id': custom_rule.get('id'),
        'is_user_rule': True,
        'blog_template': templates[0].get('name') if templates else None
    }
)
task_data = task_response.json()
task_id = task_data.get('task_id')
print("\n7. 创建爬虫任务:")
print(json.dumps(task_data, indent=2))

# 8. 等待任务完成并获取结果
print("\n8. 等待任务完成并获取结果:")
max_retries = 5
for i in range(max_retries):
    task_info_response = requests.get(
        f'{base_url}/crawler/tasks/{task_id}',
        headers=headers
    )
    task_info = task_info_response.json()
    status = task_info.get('status')
    print(f"任务状态: {status}")
    
    if status == 'success':
        print("任务完成！输出文件:")
        for file in task_info.get('output_files', []):
            print(f"- {file['name']} ({file['size']} bytes)")
        break
    elif status == 'failed':
        print(f"任务失败")
        break
    
    if i < max_retries - 1:
        print("等待任务完成...")
        time.sleep(5)  # 等待5秒后再次检查

# 9. 获取用户任务列表
tasks_response = requests.get(
    f'{base_url}/crawler/tasks',
    headers=headers
)
tasks = tasks_response.json().get('tasks', [])
print("\n9. 用户任务列表:")
print(json.dumps(tasks, indent=2))
```

## 注意事项

1. 所有示例代码都假设API服务运行在 `http://localhost:8000`，实际使用时请替换为正确的URL
2. 认证令牌有效期通常为24小时，过期后需要重新登录获取新令牌
3. 爬虫任务是异步执行的，需要定期检查任务状态
4. 创建XPath规则时，请确保XPath表达式符合标准语法
5. 使用博客模板功能需要用户组权限支持