FROM python:3.8-slim
WORKDIR /hw1
COPY . /hw1
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "./hw1.py"]
