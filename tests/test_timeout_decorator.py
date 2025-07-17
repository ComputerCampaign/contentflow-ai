#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试timeout_decorator包是否正常工作
"""

import os
import sys
import unittest
import time

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import timeout_decorator


class TestTimeoutDecorator(unittest.TestCase):
    """测试timeout_decorator功能"""
    
    def test_timeout_success(self):
        """测试不超时的情况"""
        @timeout_decorator.timeout(5)
        def function_no_timeout():
            time.sleep(1)
            return True
            
        result = function_no_timeout()
        self.assertTrue(result)
    
    def test_timeout_exception(self):
        """测试超时的情况"""
        @timeout_decorator.timeout(1)
        def function_with_timeout():
            time.sleep(2)
            return True
            
        with self.assertRaises(timeout_decorator.TimeoutError):
            function_with_timeout()


if __name__ == '__main__':
    unittest.main()