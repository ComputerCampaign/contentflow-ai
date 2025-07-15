#!/bin/bash

# 爬虫示例脚本
# 此脚本展示了crawler.py的各种使用方式和功能

# 确保当前目录是项目根目录
cd "$(dirname "$0")/.." || exit

# 示例1：基本爬取 - 使用默认配置爬取网页
echo "示例1：基本爬取 - 使用默认配置爬取网页"
echo "==================================================="
python crawler.py --url https://www.example.com

# 示例2：使用指定的XPath规则ID爬取Reddit
echo "\n\n示例2：使用指定的XPath规则ID爬取Reddit"
echo "==================================================="
python crawler.py --url https://www.reddit.com/r/pics --rule-id reddit_media

# 示例3：使用自动匹配的XPath规则爬取Twitter
echo "\n\n示例3：使用自动匹配的XPath规则爬取Twitter"
echo "==================================================="
python crawler.py --url https://twitter.com/NASA

# 示例4：使用任务ID爬取并启用博客生成
echo "\n\n示例4：使用任务ID爬取并启用博客生成"
echo "==================================================="
python crawler.py --url https://www.reddit.com/r/beautiful_houses/comments/1ly1q1u/elegant_mountain_retreat_in_the_carpathians/ --task-id elegant_mountain_retreat --rule-id general_article --enable-blog

# 示例5：使用自定义输出目录和数据目录
echo "\n\n示例5：使用自定义输出目录和数据目录"
echo "==================================================="
python crawler.py --url https://www.example.com --output custom_output --data-dir custom_data

# 示例6：启用邮件通知功能
echo "\n\n示例6：启用邮件通知功能"
echo "==================================================="
python crawler.py --url https://www.example.com --enable-email

# 示例7：设置重试次数和超时时间
echo "\n\n示例7：设置重试次数和超时时间"
echo "==================================================="
python crawler.py --url https://www.example.com --retry 5 --timeout 15

# 示例8：使用Selenium进行爬取
echo "\n\n示例8：使用Selenium进行爬取"
echo "==================================================="
python crawler.py --url https://www.example.com --use-selenium

# 示例9：列出所有可用的XPath规则
echo "\n\n示例9：列出所有可用的XPath规则"
echo "==================================================="
python crawler.py --list-rules