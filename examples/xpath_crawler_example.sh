#!/bin/bash

# XPath规则现在存储在 config/xpath/xpath_rules.json 文件中

# 示例1：使用指定的XPath规则ID爬取Reddit
echo "示例1：使用reddit_media规则爬取Reddit"
echo "==================================================="
python crawler.py --url https://www.reddit.com/r/pics --rule-id reddit_media

# 示例2：使用自动匹配的XPath规则爬取Twitter
echo "\n\n示例2：使用自动匹配的XPath规则爬取Twitter"
echo "==================================================="
python crawler.py --url https://twitter.com/NASA

# 示例3：列出所有可用的XPath规则
echo "\n\n示例3：列出所有可用的XPath规则"
echo "==================================================="
python crawler.py --list-rules