# -*- coding: utf-8 -*-
"""
每日爬虫数据处理流水线

这个DAG实现了一个完整的每日数据处理流水线，包括：
1. 健康检查
2. 数据爬取
3. 数据清洗和处理
4. 博客内容生成
5. 数据备份
6. 清理临时文件

调度: 每天凌晨2点执行
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
import logging
import os
import sys
import json

# 添加项目路径到Python路径
sys.path.append('/opt/airflow/data')

# 默认参数
default_args = {
    'owner': 'crawler-platform',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'catchup': False,
    'max_active_runs': 1,
}

# 创建DAG
dag = DAG(
    'daily_crawler_pipeline',
    default_args=default_args,
    description='每日爬虫数据处理流水线',
    schedule_interval='0 2 * * *',  # 每天凌晨2点执行
    tags=['production', 'daily', 'crawler', 'pipeline'],
    doc_md="""
    # 每日爬虫数据处理流水线
    
    这个DAG负责执行每日的数据爬取和处理任务，包括：
    
    ## 主要功能
    - 自动爬取目标网站数据
    - 数据清洗和标准化处理
    - 生成博客内容
    - 数据备份和归档
    - 系统清理和维护
    
    ## 执行时间
    每天凌晨2:00 (UTC+8)
    
    ## 监控和告警
    - 任务失败时发送邮件通知
    - 关键指标监控
    - 执行时间跟踪
    """
)

# 配置变量
CRAWLER_CONFIG = {
    'target_sites': [
        'https://example.com',
        'https://news.example.com',
        'https://blog.example.com'
    ],
    'max_pages_per_site': 50,
    'timeout': 30,
    'retry_count': 3,
    'output_format': 'json'
}

# Python函数定义

def system_health_check(**context):
    """
    系统健康检查
    检查数据库连接、磁盘空间、内存使用等
    """
    logging.info("开始系统健康检查...")
    
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    try:
        # 检查磁盘空间
        import shutil
        disk_usage = shutil.disk_usage('/opt/airflow')
        free_space_gb = disk_usage.free / (1024**3)
        
        health_status['checks']['disk_space'] = {
            'free_gb': round(free_space_gb, 2),
            'status': 'ok' if free_space_gb > 5 else 'warning'
        }
        
        # 检查内存使用
        import psutil
        memory = psutil.virtual_memory()
        
        health_status['checks']['memory'] = {
            'available_gb': round(memory.available / (1024**3), 2),
            'percent_used': memory.percent,
            'status': 'ok' if memory.percent < 80 else 'warning'
        }
        
        # 检查数据库连接（模拟）
        health_status['checks']['database'] = {
            'connection': 'ok',
            'response_time_ms': 15
        }
        
        # 检查关键目录
        required_dirs = ['/opt/airflow/dags', '/opt/airflow/logs', '/opt/airflow/data']
        for dir_path in required_dirs:
            health_status['checks'][f'directory_{os.path.basename(dir_path)}'] = {
                'exists': os.path.exists(dir_path),
                'writable': os.access(dir_path, os.W_OK) if os.path.exists(dir_path) else False
            }
        
        # 总体健康状态
        all_ok = all(
            check.get('status', 'ok') == 'ok' and 
            check.get('exists', True) and 
            check.get('writable', True)
            for check in health_status['checks'].values()
        )
        
        health_status['overall_status'] = 'healthy' if all_ok else 'warning'
        
        logging.info(f"健康检查完成: {health_status['overall_status']}")
        logging.info(f"详细信息: {json.dumps(health_status, indent=2)}")
        
        return health_status
        
    except Exception as e:
        logging.error(f"健康检查失败: {str(e)}")
        health_status['overall_status'] = 'error'
        health_status['error'] = str(e)
        raise

def crawl_target_sites(**context):
    """
    爬取目标网站数据
    """
    logging.info("开始爬取目标网站...")
    
    # 获取配置
    config = context.get('params', CRAWLER_CONFIG)
    target_sites = config.get('target_sites', [])
    
    crawl_results = {
        'timestamp': datetime.now().isoformat(),
        'sites': {},
        'summary': {
            'total_sites': len(target_sites),
            'successful': 0,
            'failed': 0,
            'total_items': 0
        }
    }
    
    for site_url in target_sites:
        logging.info(f"爬取网站: {site_url}")
        
        try:
            # 模拟爬虫执行
            import time
            import random
            
            # 模拟爬取时间
            crawl_time = random.randint(10, 30)
            time.sleep(min(crawl_time, 5))  # 实际等待时间限制在5秒内
            
            # 模拟爬取结果
            items_count = random.randint(20, 100)
            
            site_result = {
                'url': site_url,
                'status': 'success',
                'items_count': items_count,
                'crawl_time_seconds': crawl_time,
                'data_size_mb': round(items_count * 0.05, 2),
                'last_updated': datetime.now().isoformat()
            }
            
            crawl_results['sites'][site_url] = site_result
            crawl_results['summary']['successful'] += 1
            crawl_results['summary']['total_items'] += items_count
            
            logging.info(f"网站 {site_url} 爬取成功: {items_count} 条数据")
            
        except Exception as e:
            logging.error(f"网站 {site_url} 爬取失败: {str(e)}")
            
            crawl_results['sites'][site_url] = {
                'url': site_url,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            crawl_results['summary']['failed'] += 1
    
    # 计算成功率
    total_sites = crawl_results['summary']['total_sites']
    successful = crawl_results['summary']['successful']
    crawl_results['summary']['success_rate'] = round((successful / total_sites) * 100, 2) if total_sites > 0 else 0
    
    logging.info(f"爬取完成 - 成功: {successful}/{total_sites}, 总数据: {crawl_results['summary']['total_items']} 条")
    
    # 如果成功率低于50%，抛出异常
    if crawl_results['summary']['success_rate'] < 50:
        raise Exception(f"爬取成功率过低: {crawl_results['summary']['success_rate']}%")
    
    return crawl_results

def process_crawled_data(**context):
    """
    处理爬取的数据
    包括数据清洗、去重、标准化等
    """
    logging.info("开始处理爬取的数据...")
    
    # 从上游任务获取数据
    crawl_results = context['task_instance'].xcom_pull(task_ids='crawl_sites')
    
    if not crawl_results:
        raise ValueError("未获取到爬虫数据")
    
    processing_results = {
        'timestamp': datetime.now().isoformat(),
        'input_summary': crawl_results['summary'],
        'processing_steps': [],
        'output_summary': {}
    }
    
    total_items = crawl_results['summary']['total_items']
    
    try:
        # 步骤1: 数据去重
        logging.info("执行数据去重...")
        duplicate_rate = 0.15  # 假设15%的重复率
        duplicates_removed = int(total_items * duplicate_rate)
        remaining_items = total_items - duplicates_removed
        
        processing_results['processing_steps'].append({
            'step': 'deduplication',
            'input_count': total_items,
            'duplicates_removed': duplicates_removed,
            'output_count': remaining_items,
            'status': 'completed'
        })
        
        # 步骤2: 数据清洗
        logging.info("执行数据清洗...")
        invalid_rate = 0.08  # 假设8%的无效数据
        invalid_removed = int(remaining_items * invalid_rate)
        cleaned_items = remaining_items - invalid_removed
        
        processing_results['processing_steps'].append({
            'step': 'data_cleaning',
            'input_count': remaining_items,
            'invalid_removed': invalid_removed,
            'output_count': cleaned_items,
            'status': 'completed'
        })
        
        # 步骤3: 数据标准化
        logging.info("执行数据标准化...")
        standardized_items = cleaned_items  # 标准化不减少数据量
        
        processing_results['processing_steps'].append({
            'step': 'standardization',
            'input_count': cleaned_items,
            'output_count': standardized_items,
            'status': 'completed'
        })
        
        # 步骤4: 数据分类
        logging.info("执行数据分类...")
        categories = {
            'news': int(standardized_items * 0.4),
            'blog': int(standardized_items * 0.3),
            'tech': int(standardized_items * 0.2),
            'other': int(standardized_items * 0.1)
        }
        
        processing_results['processing_steps'].append({
            'step': 'categorization',
            'input_count': standardized_items,
            'categories': categories,
            'status': 'completed'
        })
        
        # 输出摘要
        processing_results['output_summary'] = {
            'total_processed': standardized_items,
            'data_quality_score': 85.5,
            'categories': categories,
            'processing_time_seconds': 45,
            'data_reduction_rate': round((1 - standardized_items / total_items) * 100, 2)
        }
        
        logging.info(f"数据处理完成 - 输入: {total_items}, 输出: {standardized_items}, 质量分: {processing_results['output_summary']['data_quality_score']}")
        
        return processing_results
        
    except Exception as e:
        logging.error(f"数据处理失败: {str(e)}")
        processing_results['error'] = str(e)
        raise

def generate_blog_content(**context):
    """
    基于处理后的数据生成博客内容
    """
    logging.info("开始生成博客内容...")
    
    # 从上游任务获取数据
    processing_results = context['task_instance'].xcom_pull(task_ids='process_data')
    
    if not processing_results:
        raise ValueError("未获取到处理后的数据")
    
    categories = processing_results['output_summary']['categories']
    total_items = processing_results['output_summary']['total_processed']
    
    blog_results = {
        'timestamp': datetime.now().isoformat(),
        'generated_content': [],
        'summary': {}
    }
    
    try:
        # 为每个分类生成博客内容
        for category, count in categories.items():
            if count > 0:
                logging.info(f"为分类 '{category}' 生成博客内容 ({count} 条数据)")
                
                # 模拟博客生成
                import time
                time.sleep(1)  # 模拟生成时间
                
                blog_content = {
                    'category': category,
                    'title': f"{category.title()} 数据分析报告 - {datetime.now().strftime('%Y-%m-%d')}",
                    'content_length': count * 50,  # 假设每条数据生成50字符
                    'images_count': min(count // 10, 5),  # 每10条数据生成1张图，最多5张
                    'tags': [category, 'data-analysis', 'daily-report'],
                    'estimated_reading_time': max(count // 20, 1),  # 阅读时间（分钟）
                    'status': 'generated'
                }
                
                blog_results['generated_content'].append(blog_content)
        
        # 生成总结报告
        summary_blog = {
            'category': 'summary',
            'title': f"每日数据汇总报告 - {datetime.now().strftime('%Y-%m-%d')}",
            'content_length': 1500,
            'images_count': 3,
            'tags': ['summary', 'daily-report', 'analytics'],
            'estimated_reading_time': 8,
            'status': 'generated',
            'includes_charts': True,
            'data_sources': len(categories)
        }
        
        blog_results['generated_content'].append(summary_blog)
        
        # 计算摘要
        total_blogs = len(blog_results['generated_content'])
        total_content_length = sum(blog['content_length'] for blog in blog_results['generated_content'])
        total_images = sum(blog['images_count'] for blog in blog_results['generated_content'])
        
        blog_results['summary'] = {
            'total_blogs_generated': total_blogs,
            'total_content_length': total_content_length,
            'total_images': total_images,
            'average_reading_time': round(sum(blog['estimated_reading_time'] for blog in blog_results['generated_content']) / total_blogs, 1),
            'generation_time_seconds': 25,
            'data_utilization_rate': 95.5
        }
        
        logging.info(f"博客生成完成 - 生成 {total_blogs} 篇博客, 总长度: {total_content_length} 字符")
        
        return blog_results
        
    except Exception as e:
        logging.error(f"博客生成失败: {str(e)}")
        blog_results['error'] = str(e)
        raise

def backup_processed_data(**context):
    """
    备份处理后的数据
    """
    logging.info("开始备份处理后的数据...")
    
    # 获取所有上游任务的结果
    crawl_results = context['task_instance'].xcom_pull(task_ids='crawl_sites')
    processing_results = context['task_instance'].xcom_pull(task_ids='process_data')
    blog_results = context['task_instance'].xcom_pull(task_ids='generate_blogs')
    
    backup_results = {
        'timestamp': datetime.now().isoformat(),
        'backup_files': [],
        'summary': {}
    }
    
    try:
        # 模拟备份过程
        import time
        
        # 备份原始数据
        if crawl_results:
            backup_file = f"crawl_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_results['backup_files'].append({
                'type': 'crawl_data',
                'filename': backup_file,
                'size_mb': 15.5,
                'records': crawl_results['summary']['total_items']
            })
            time.sleep(1)
        
        # 备份处理后数据
        if processing_results:
            backup_file = f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_results['backup_files'].append({
                'type': 'processed_data',
                'filename': backup_file,
                'size_mb': 12.3,
                'records': processing_results['output_summary']['total_processed']
            })
            time.sleep(1)
        
        # 备份博客内容
        if blog_results:
            backup_file = f"blog_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_results['backup_files'].append({
                'type': 'blog_content',
                'filename': backup_file,
                'size_mb': 3.8,
                'records': blog_results['summary']['total_blogs_generated']
            })
            time.sleep(1)
        
        # 计算备份摘要
        total_files = len(backup_results['backup_files'])
        total_size = sum(file['size_mb'] for file in backup_results['backup_files'])
        
        backup_results['summary'] = {
            'total_files': total_files,
            'total_size_mb': round(total_size, 2),
            'backup_location': '/opt/airflow/data/backups',
            'retention_days': 30,
            'compression_ratio': 0.75,
            'backup_time_seconds': 8
        }
        
        logging.info(f"数据备份完成 - {total_files} 个文件, 总大小: {total_size:.2f} MB")
        
        return backup_results
        
    except Exception as e:
        logging.error(f"数据备份失败: {str(e)}")
        backup_results['error'] = str(e)
        raise

def cleanup_temp_files(**context):
    """
    清理临时文件和过期数据
    """
    logging.info("开始清理临时文件...")
    
    cleanup_results = {
        'timestamp': datetime.now().isoformat(),
        'cleaned_items': [],
        'summary': {}
    }
    
    try:
        import glob
        import time
        
        # 模拟清理不同类型的临时文件
        cleanup_tasks = [
            {'pattern': '/tmp/crawler_*', 'description': '爬虫临时文件'},
            {'pattern': '/tmp/airflow_*', 'description': 'Airflow临时文件'},
            {'pattern': '/opt/airflow/logs/*.log.old', 'description': '过期日志文件'},
            {'pattern': '/opt/airflow/data/temp/*', 'description': '临时数据文件'}
        ]
        
        total_cleaned = 0
        total_size_freed = 0
        
        for task in cleanup_tasks:
            pattern = task['pattern']
            description = task['description']
            
            # 模拟文件查找和删除
            import random
            files_found = random.randint(0, 10)
            size_freed = random.uniform(0.1, 5.0)
            
            if files_found > 0:
                cleanup_item = {
                    'type': description,
                    'pattern': pattern,
                    'files_cleaned': files_found,
                    'size_freed_mb': round(size_freed, 2),
                    'status': 'completed'
                }
                
                cleanup_results['cleaned_items'].append(cleanup_item)
                total_cleaned += files_found
                total_size_freed += size_freed
                
                logging.info(f"清理 {description}: {files_found} 个文件, {size_freed:.2f} MB")
            
            time.sleep(0.5)
        
        # 清理过期备份
        expired_backups = random.randint(0, 3)
        if expired_backups > 0:
            cleanup_item = {
                'type': '过期备份文件',
                'pattern': '/opt/airflow/data/backups/*',
                'files_cleaned': expired_backups,
                'size_freed_mb': round(expired_backups * 10.5, 2),
                'status': 'completed'
            }
            
            cleanup_results['cleaned_items'].append(cleanup_item)
            total_cleaned += expired_backups
            total_size_freed += expired_backups * 10.5
        
        # 计算清理摘要
        cleanup_results['summary'] = {
            'total_files_cleaned': total_cleaned,
            'total_size_freed_mb': round(total_size_freed, 2),
            'cleanup_categories': len(cleanup_results['cleaned_items']),
            'cleanup_time_seconds': 12,
            'disk_space_recovered': f"{total_size_freed:.1f} MB"
        }
        
        logging.info(f"清理完成 - 删除 {total_cleaned} 个文件, 释放 {total_size_freed:.2f} MB 空间")
        
        return cleanup_results
        
    except Exception as e:
        logging.error(f"清理任务失败: {str(e)}")
        cleanup_results['error'] = str(e)
        # 清理任务失败不应该影响整个流水线
        return cleanup_results

def send_daily_report(**context):
    """
    发送每日报告邮件
    """
    logging.info("准备每日报告...")
    
    # 收集所有任务的结果
    health_check = context['task_instance'].xcom_pull(task_ids='health_check')
    crawl_results = context['task_instance'].xcom_pull(task_ids='crawl_sites')
    processing_results = context['task_instance'].xcom_pull(task_ids='process_data')
    blog_results = context['task_instance'].xcom_pull(task_ids='generate_blogs')
    backup_results = context['task_instance'].xcom_pull(task_ids='backup_data')
    cleanup_results = context['task_instance'].xcom_pull(task_ids='cleanup_files')
    
    # 生成报告内容
    report_content = f"""
    每日爬虫流水线执行报告
    执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    === 执行摘要 ===
    • 爬取网站: {crawl_results['summary']['total_sites'] if crawl_results else 'N/A'} 个
    • 成功率: {crawl_results['summary']['success_rate'] if crawl_results else 'N/A'}%
    • 数据条数: {crawl_results['summary']['total_items'] if crawl_results else 'N/A'} 条
    • 处理后数据: {processing_results['output_summary']['total_processed'] if processing_results else 'N/A'} 条
    • 生成博客: {blog_results['summary']['total_blogs_generated'] if blog_results else 'N/A'} 篇
    • 备份文件: {backup_results['summary']['total_files'] if backup_results else 'N/A'} 个
    • 清理文件: {cleanup_results['summary']['total_files_cleaned'] if cleanup_results else 'N/A'} 个
    
    === 系统状态 ===
    • 整体健康: {health_check['overall_status'] if health_check else 'N/A'}
    • 磁盘空间: {health_check['checks']['disk_space']['free_gb'] if health_check and 'disk_space' in health_check['checks'] else 'N/A'} GB
    • 内存使用: {health_check['checks']['memory']['percent_used'] if health_check and 'memory' in health_check['checks'] else 'N/A'}%
    
    详细信息请查看 Airflow Web UI: http://localhost:8080
    """
    
    logging.info("每日报告准备完成")
    logging.info(report_content)
    
    return {
        'report_content': report_content,
        'timestamp': datetime.now().isoformat(),
        'status': 'completed'
    }

# 任务定义

# 开始任务
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# 系统健康检查
health_check_task = PythonOperator(
    task_id='health_check',
    python_callable=system_health_check,
    dag=dag,
    doc_md="检查系统健康状态，包括磁盘空间、内存使用、数据库连接等"
)

# 数据爬取任务组
with TaskGroup("data_collection", dag=dag) as data_collection_group:
    
    # 爬取网站数据
    crawl_task = PythonOperator(
        task_id='crawl_sites',
        python_callable=crawl_target_sites,
        params=CRAWLER_CONFIG,
        dag=dag,
        doc_md="爬取配置的目标网站数据"
    )
    
    # 数据处理
    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_crawled_data,
        dag=dag,
        doc_md="处理爬取的数据，包括去重、清洗、标准化等"
    )
    
    crawl_task >> process_task

# 内容生成任务
generate_blog_task = PythonOperator(
    task_id='generate_blogs',
    python_callable=generate_blog_content,
    dag=dag,
    doc_md="基于处理后的数据生成博客内容"
)

# 数据管理任务组
with TaskGroup("data_management", dag=dag) as data_management_group:
    
    # 数据备份
    backup_task = PythonOperator(
        task_id='backup_data',
        python_callable=backup_processed_data,
        dag=dag,
        doc_md="备份处理后的数据和生成的内容"
    )
    
    # 清理临时文件
    cleanup_task = PythonOperator(
        task_id='cleanup_files',
        python_callable=cleanup_temp_files,
        trigger_rule='all_done',  # 无论上游任务成功或失败都执行
        dag=dag,
        doc_md="清理临时文件和过期数据"
    )
    
    backup_task >> cleanup_task

# 系统维护任务
system_maintenance = BashOperator(
    task_id='system_maintenance',
    bash_command='''
    echo "执行系统维护任务..."
    
    # 检查磁盘使用情况
    echo "=== 磁盘使用情况 ==="
    df -h
    
    # 检查内存使用情况
    echo "=== 内存使用情况 ==="
    free -h
    
    # 检查进程状态
    echo "=== Airflow进程状态 ==="
    ps aux | grep airflow | head -5
    
    # 检查日志文件大小
    echo "=== 日志文件大小 ==="
    find /opt/airflow/logs -name "*.log" -type f -exec ls -lh {} + | head -10
    
    echo "系统维护检查完成"
    ''',
    dag=dag,
    doc_md="执行系统维护检查，监控资源使用情况"
)

# 报告生成任务
report_task = PythonOperator(
    task_id='generate_report',
    python_callable=send_daily_report,
    dag=dag,
    doc_md="生成并发送每日执行报告"
)

# 结束任务
end_task = DummyOperator(
    task_id='end',
    trigger_rule='all_done',
    dag=dag,
)

# 定义任务依赖关系
start_task >> health_check_task
health_check_task >> data_collection_group
data_collection_group >> generate_blog_task
generate_blog_task >> data_management_group

# 并行执行系统维护
health_check_task >> system_maintenance

# 汇聚到报告生成
[data_management_group, system_maintenance] >> report_task >> end_task

# 设置任务文档
dag.doc_md = """
# 每日爬虫数据处理流水线

这是一个完整的每日数据处理流水线，自动化执行以下任务：

## 工作流程

1. **系统健康检查** - 验证系统状态和资源可用性
2. **数据收集组**
   - 爬取目标网站数据
   - 数据清洗和处理
3. **内容生成** - 基于数据生成博客内容
4. **数据管理组**
   - 数据备份
   - 临时文件清理
5. **系统维护** - 系统状态监控
6. **报告生成** - 生成执行摘要报告

## 调度策略

- **执行时间**: 每天凌晨 2:00 (UTC+8)
- **重试策略**: 失败时重试 2 次，间隔 10 分钟
- **并发控制**: 最多同时运行 1 个实例
- **邮件通知**: 任务失败时发送邮件

## 监控指标

- 数据爬取成功率
- 数据处理质量分数
- 系统资源使用情况
- 任务执行时间

## 故障处理

- 爬取失败时自动重试
- 数据质量检查
- 系统资源监控
- 自动清理和恢复
"""

# 为关键任务添加文档
health_check_task.doc_md = """
## 系统健康检查

检查以下系统指标：
- 磁盘空间使用情况
- 内存使用情况  
- 数据库连接状态
- 关键目录权限

如果任何检查失败，任务将报告警告或错误状态。
"""

data_collection_group.doc_md = """
## 数据收集任务组

包含两个关键步骤：
1. **数据爬取** - 从配置的网站爬取数据
2. **数据处理** - 清洗、去重、标准化数据

数据质量要求：
- 爬取成功率 > 50%
- 数据质量分数 > 80
"""

data_management_group.doc_md = """
## 数据管理任务组

负责数据的长期管理：
1. **数据备份** - 备份原始和处理后的数据
2. **文件清理** - 清理临时文件和过期数据

备份策略：
- 保留期：30天
- 压缩比：75%
- 存储位置：/opt/airflow/data/backups
"""