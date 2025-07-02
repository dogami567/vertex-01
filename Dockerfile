# 使用官方的、轻量级的Python 3.11-slim作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
# 我们先复制这个文件并安装依赖，这样可以利用Docker的缓存机制
# 只要requirements.txt不变，下次构建时就会跳过这一步，加快速度
COPY requirements.txt .

# 安装依赖
# --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码到工作目录
COPY . .

# 将应用凭据文件路径设置为环境变量
# 我们期望在运行容器时，将本地的凭据文件挂载到这个路径
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp_credentials.json

# 暴露应用运行的端口
EXPOSE 5000

# 容器启动时运行的命令
CMD ["python", "simplest.py"] 