FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ../user-service ./

EXPOSE 8007

CMD [ "python", "main.py" ]