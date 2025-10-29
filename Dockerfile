# 使用稳定版 Python 镜像
FROM python:3.14-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖（分两步确保PyTorch安装成功）
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
 && pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 复制代码和模型文件
COPY app.py model.py mnist_cnn.pth ./

EXPOSE 5000

CMD ["python", "app.py"]
