FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ../time-sheet-service ./

EXPOSE 8006

CMD [ "python", "main.py" ]