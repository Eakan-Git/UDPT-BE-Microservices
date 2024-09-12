FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ../ticket-service ./

EXPOSE 8005

CMD [ "python", "main.py" ]