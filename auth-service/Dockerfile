FROM python:3.10-slim

WORKDIR /app

COPY ../../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ../auth-service ./

EXPOSE 8003

CMD [ "python", "main.py" ]