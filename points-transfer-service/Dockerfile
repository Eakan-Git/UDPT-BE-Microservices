FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./points-transfer-service ./

EXPOSE 8004

CMD [ "python", "main.py" ]