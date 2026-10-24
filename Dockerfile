FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY src/ /app/src/
CMD ["python", "src/main.py"]