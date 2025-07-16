#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试XPath规则匹配和应用
"""

import sys
import argparse
import json
from crawler_utils.xpath_manager import XPathManager
from config import config

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试XPath规则匹配和应用")
    parser.add_argument("--url", default="https://www.example.com", help="要测试的网页URL")
    parser.add_argument("--rule-id", help="指定要测试的规则ID")
    parser.add_argument("--list-rules", action="store_true", help="列出所有可用的规则")
    
    args = parser.parse_args()
    
    # 获取XPath配置
    xpath_config = config.get('crawler', 'xpath_config', {})
    if not xpath_config.get('enabled', False):
        print("XPath功能未启用，请在config.json中启用")
        sys.exit(1)
    
    # 创建XPathManager实例
    xpath_manager = XPathManager()
    
    # 列出所有规则
    if args.list_rules:
        print("可用的XPath规则:")
        for rule in xpath_manager.rules:
            print(f"规则ID: {rule.get('id', '未知')}")
            print(f"  名称: {rule.get('name', '无名称')}")
            print(f"  描述: {rule.get('description', '无描述')}")
            print(f"  域名模式: {rule.get('domain_patterns', [])}")
            print(f"  XPath: {rule.get('xpath', '无XPath')}")
            print()
        return
    
    # 测试URL匹配规则
    if args.url:
        print(f"测试URL: {args.url}")
        if args.rule_id:
            # 使用指定的规则
            rule = xpath_manager.get_rule_by_id(args.rule_id)
            if not rule:
                print(f"错误: 规则ID '{args.rule_id}'不存在")
                sys.exit(1)
            print(f"使用指定的规则: {args.rule_id}")
        else:
            # 使用默认规则
            rule = xpath_manager.get_rule_by_id(xpath_manager.default_rule_id)
            if rule:
                print(f"使用默认规则: {rule.get('id')}")
            else:
                print("未找到默认规则")
        
        # 打印规则详情
        print("\n规则详情:")
        print(json.dumps(rule, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()