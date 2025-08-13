#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XPath配置同步服务
实现数据库与JSON文件的双向同步机制
确保crawler/config/xpath/xpath_rules.json与数据库中的XPath配置保持一致
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models.xpath import XPathConfig
from backend.database import get_db_session
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON文件路径
XPATH_JSON_FILE = os.path.join(
    os.path.dirname(__file__), 
    '..', '..', 'crawler', 'config', 'xpath', 'xpath_rules.json'
)


class XPathSyncService:
    """XPath配置同步服务"""
    
    def __init__(self):
        self.json_file_path = XPATH_JSON_FILE
        self.ensure_json_file_exists()
    
    def ensure_json_file_exists(self):
        """确保JSON文件存在"""
        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
        
        if not os.path.exists(self.json_file_path):
            # 创建空的JSON文件
            empty_data = {"rules": []}
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, ensure_ascii=False, indent=4)
            logger.info(f"创建空的XPath规则文件: {self.json_file_path}")
    
    def load_json_rules(self) -> Dict:
        """从JSON文件加载规则"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"加载JSON规则失败: {str(e)}")
            return {"rules": []}
    
    def save_json_rules(self, data: Dict) -> bool:
        """保存规则到JSON文件"""
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"XPath规则已保存到: {self.json_file_path}")
            return True
        except Exception as e:
            logger.error(f"保存JSON规则失败: {str(e)}")
            return False
    
    def db_to_json_format(self, xpath_config: XPathConfig) -> Dict:
        """将数据库XPath配置转换为JSON格式"""
        rule_data = {
            "id": xpath_config.rule_id,
            "name": xpath_config.name,
            "description": xpath_config.description or "",
            "domain_patterns": xpath_config.domain_patterns or [],
            "xpath": xpath_config.xpath,
            "rule_type": xpath_config.rule_type,
            "field_name": xpath_config.field_name
        }
        
        # 添加扩展配置
        if xpath_config.comment_xpath:
            rule_data["comment_xpath"] = xpath_config.comment_xpath
        
        return rule_data
    
    def json_to_db_format(self, rule_data: Dict, user_id: str) -> Dict:
        """将JSON规则转换为数据库格式"""
        db_data = {
            "rule_id": rule_data.get("id"),
            "name": rule_data.get("name"),
            "description": rule_data.get("description", ""),
            "domain_patterns": rule_data.get("domain_patterns", []),
            "xpath": rule_data.get("xpath"),
            "rule_type": rule_data.get("rule_type"),
            "field_name": rule_data.get("field_name"),
            "user_id": user_id,
            "status": "active",
            "is_public": True  # JSON文件中的规则默认为公开
        }
        
        # 添加扩展配置
        if "comment_xpath" in rule_data:
            db_data["comment_xpath"] = rule_data["comment_xpath"]
        
        return db_data
    
    def sync_db_to_json(self, session: Optional[Session] = None) -> Tuple[bool, str]:
        """将数据库中的XPath配置同步到JSON文件"""
        try:
            if session is None:
                session = get_db_session()
                should_close = True
            else:
                should_close = False
            
            # 查询所有活跃的公开XPath配置
            xpath_configs = session.query(XPathConfig).filter(
                XPathConfig.status == 'active',
                XPathConfig.is_public == True
            ).all()
            
            # 构建JSON数据
            json_data = {
                "rules": []
            }
            
            for config in xpath_configs:
                rule_data = self.db_to_json_format(config)
                json_data["rules"].append(rule_data)
            
            # 保存到JSON文件
            if self.save_json_rules(json_data):
                message = f"成功同步 {len(json_data['rules'])} 个规则到JSON文件"
                logger.info(message)
                
                if should_close:
                    session.close()
                
                return True, message
            else:
                if should_close:
                    session.close()
                return False, "保存JSON文件失败"
        
        except Exception as e:
            error_msg = f"数据库到JSON同步失败: {str(e)}"
            logger.error(error_msg)
            if 'session' in locals() and should_close:
                session.close()
            return False, error_msg
    
    def sync_json_to_db(self, user_id: str, session: Optional[Session] = None) -> Tuple[bool, str]:
        """将JSON文件中的规则同步到数据库"""
        try:
            if session is None:
                session = get_db_session()
                should_close = True
            else:
                should_close = False
            
            # 加载JSON规则
            json_data = self.load_json_rules()
            rules = json_data.get("rules", [])
            
            if not rules:
                message = "JSON文件中没有规则需要同步"
                logger.info(message)
                if should_close:
                    session.close()
                return True, message
            
            created_count = 0
            updated_count = 0
            
            for rule_data in rules:
                rule_id = rule_data.get("id")
                if not rule_id:
                    logger.warning(f"跳过没有ID的规则: {rule_data.get('name', 'Unknown')}")
                    continue
                
                # 检查规则是否已存在
                existing_config = session.query(XPathConfig).filter_by(rule_id=rule_id).first()
                
                if existing_config:
                    # 更新现有规则
                    db_data = self.json_to_db_format(rule_data, user_id)
                    for key, value in db_data.items():
                        if key != 'rule_id':  # 不更新主键
                            setattr(existing_config, key, value)
                    existing_config.updated_at = datetime.utcnow()
                    updated_count += 1
                    logger.info(f"更新XPath规则: {rule_id}")
                else:
                    # 创建新规则
                    db_data = self.json_to_db_format(rule_data, user_id)
                    new_config = XPathConfig(**db_data)
                    session.add(new_config)
                    created_count += 1
                    logger.info(f"创建XPath规则: {rule_id}")
            
            # 提交更改
            session.commit()
            
            message = f"JSON到数据库同步完成: 创建 {created_count} 个，更新 {updated_count} 个规则"
            logger.info(message)
            
            if should_close:
                session.close()
            
            return True, message
        
        except Exception as e:
            error_msg = f"JSON到数据库同步失败: {str(e)}"
            logger.error(error_msg)
            if 'session' in locals():
                session.rollback()
                if should_close:
                    session.close()
            return False, error_msg
    
    def bidirectional_sync(self, user_id: str, session: Optional[Session] = None) -> Tuple[bool, str]:
        """双向同步：先从JSON同步到数据库，再从数据库同步到JSON"""
        try:
            if session is None:
                session = get_db_session()
                should_close = True
            else:
                should_close = False
            
            # 1. JSON -> 数据库
            json_to_db_success, json_to_db_msg = self.sync_json_to_db(user_id, session)
            if not json_to_db_success:
                if should_close:
                    session.close()
                return False, f"JSON到数据库同步失败: {json_to_db_msg}"
            
            # 2. 数据库 -> JSON
            db_to_json_success, db_to_json_msg = self.sync_db_to_json(session)
            if not db_to_json_success:
                if should_close:
                    session.close()
                return False, f"数据库到JSON同步失败: {db_to_json_msg}"
            
            message = f"双向同步完成: {json_to_db_msg}; {db_to_json_msg}"
            logger.info(message)
            
            if should_close:
                session.close()
            
            return True, message
        
        except Exception as e:
            error_msg = f"双向同步失败: {str(e)}"
            logger.error(error_msg)
            if 'session' in locals() and should_close:
                session.close()
            return False, error_msg
    
    def validate_rule_data(self, rule_data: Dict) -> Tuple[bool, str]:
        """验证规则数据的完整性"""
        required_fields = ['id', 'name', 'xpath', 'rule_type', 'field_name']
        
        for field in required_fields:
            if not rule_data.get(field):
                return False, f"缺少必需字段: {field}"
        
        # 验证规则类型
        valid_rule_types = ['text', 'image', 'link', 'data']
        if rule_data.get('rule_type') not in valid_rule_types:
            return False, f"无效的规则类型: {rule_data.get('rule_type')}，有效值: {valid_rule_types}"
        
        # 验证域名模式
        domain_patterns = rule_data.get('domain_patterns', [])
        if not isinstance(domain_patterns, list):
            return False, "domain_patterns必须是数组"
        
        return True, "验证通过"
    
    def add_rule_to_json(self, rule_data: Dict) -> Tuple[bool, str]:
        """向JSON文件添加新规则"""
        try:
            # 验证规则数据
            is_valid, validation_msg = self.validate_rule_data(rule_data)
            if not is_valid:
                return False, validation_msg
            
            # 加载现有规则
            json_data = self.load_json_rules()
            
            # 检查规则ID是否已存在
            existing_ids = [rule.get('id') for rule in json_data.get('rules', [])]
            if rule_data.get('id') in existing_ids:
                return False, f"规则ID已存在: {rule_data.get('id')}"
            
            # 添加新规则
            json_data['rules'].append(rule_data)
            
            # 保存文件
            if self.save_json_rules(json_data):
                message = f"成功添加规则到JSON文件: {rule_data.get('id')}"
                logger.info(message)
                return True, message
            else:
                return False, "保存JSON文件失败"
        
        except Exception as e:
            error_msg = f"添加规则到JSON失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def remove_rule_from_json(self, rule_id: str) -> Tuple[bool, str]:
        """从JSON文件移除规则"""
        try:
            # 加载现有规则
            json_data = self.load_json_rules()
            rules = json_data.get('rules', [])
            
            # 查找并移除规则
            original_count = len(rules)
            json_data['rules'] = [rule for rule in rules if rule.get('id') != rule_id]
            
            if len(json_data['rules']) == original_count:
                return False, f"未找到规则ID: {rule_id}"
            
            # 保存文件
            if self.save_json_rules(json_data):
                message = f"成功从JSON文件移除规则: {rule_id}"
                logger.info(message)
                return True, message
            else:
                return False, "保存JSON文件失败"
        
        except Exception as e:
            error_msg = f"从JSON移除规则失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_json_file_info(self) -> Dict:
        """获取JSON文件信息"""
        try:
            json_data = self.load_json_rules()
            rules = json_data.get('rules', [])
            
            # 统计信息
            rule_types = {}
            for rule in rules:
                rule_type = rule.get('rule_type', 'unknown')
                rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
            
            # 文件信息
            file_info = {
                'file_path': self.json_file_path,
                'exists': os.path.exists(self.json_file_path),
                'total_rules': len(rules),
                'rule_types': rule_types,
                'rule_ids': [rule.get('id') for rule in rules]
            }
            
            if file_info['exists']:
                stat = os.stat(self.json_file_path)
                file_info['file_size'] = stat.st_size
                file_info['last_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            return file_info
        
        except Exception as e:
            logger.error(f"获取JSON文件信息失败: {str(e)}")
            return {
                'file_path': self.json_file_path,
                'exists': False,
                'error': str(e)
            }


# 全局同步服务实例
xpath_sync_service = XPathSyncService()


# 便捷函数
def sync_xpath_db_to_json(session: Optional[Session] = None) -> Tuple[bool, str]:
    """便捷函数：数据库到JSON同步"""
    return xpath_sync_service.sync_db_to_json(session)


def sync_xpath_json_to_db(user_id: str, session: Optional[Session] = None) -> Tuple[bool, str]:
    """便捷函数：JSON到数据库同步"""
    return xpath_sync_service.sync_json_to_db(user_id, session)


def sync_xpath_bidirectional(user_id: str, session: Optional[Session] = None) -> Tuple[bool, str]:
    """便捷函数：双向同步"""
    return xpath_sync_service.bidirectional_sync(user_id, session)


def add_xpath_rule_to_json(rule_data: Dict) -> Tuple[bool, str]:
    """便捷函数：添加规则到JSON"""
    return xpath_sync_service.add_rule_to_json(rule_data)


def remove_xpath_rule_from_json(rule_id: str) -> Tuple[bool, str]:
    """便捷函数：从JSON移除规则"""
    return xpath_sync_service.remove_rule_from_json(rule_id)


def get_xpath_json_info() -> Dict:
    """便捷函数：获取JSON文件信息"""
    return xpath_sync_service.get_json_file_info()


if __name__ == "__main__":
    # 测试同步服务
    print("🔄 测试XPath配置同步服务")
    
    # 获取JSON文件信息
    info = get_xpath_json_info()
    print(f"📄 JSON文件信息: {json.dumps(info, indent=2, ensure_ascii=False)}")
    
    # 测试双向同步
    success, message = sync_xpath_bidirectional('admin-user-id-001')
    print(f"🔄 双向同步结果: {success} - {message}")