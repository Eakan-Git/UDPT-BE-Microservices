FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./voucher-service ./

EXPOSE 8009

CMD [ "python", "main.py" ]