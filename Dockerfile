FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 先装依赖以利用 Docker layer cache
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 再复制代码
COPY . /app

# 确保 SQLite 默认路径存在（见 config.py：instance/history_heroes.db）
RUN mkdir -p /app/instance

EXPOSE 5000

CMD ["python", "run.py"]
