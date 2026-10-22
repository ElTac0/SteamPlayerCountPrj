FROM python:3.12-slim

COPY requirements.txt /tmp
WORKDIR /tmp
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_loop.py"]
