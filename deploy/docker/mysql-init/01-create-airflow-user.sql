-- 创建 Airflow 数据库
CREATE DATABASE IF NOT EXISTS crawler_airflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 Airflow 用户
CREATE USER IF NOT EXISTS 'crawler_airflow_usage'@'%' IDENTIFIED BY 'crawler_airflow_usage_Pwd123!';

-- 授权 Airflow 用户对 Airflow 数据库的所有权限
GRANT ALL PRIVILEGES ON crawler_airflow_db.* TO 'crawler_airflow_usage'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示创建结果
SELECT 'Airflow database and user created successfully' AS status;