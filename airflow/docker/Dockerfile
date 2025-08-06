FROM airflow:2.9.3

# 使用airflow用户
USER airflow

# 配置pip使用国内镜像源并安装Python依赖
COPY requirements.txt /tmp/requirements.txt
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip install --no-cache-dir --trusted-host pypi.tuna.tsinghua.edu.cn -r /tmp/requirements.txt

# 复制配置文件
COPY airflow.cfg /opt/airflow/airflow.cfg
COPY webserver_config.py /opt/airflow/webserver_config.py

# 复制自定义脚本
COPY entrypoint.sh /opt/airflow/entrypoint.sh

# 设置工作目录
WORKDIR /opt/airflow

# 设置入口点
ENTRYPOINT ["/opt/airflow/entrypoint.sh"]