FROM python:3.5
ENV FLASK_APP server/server.py

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["flask", "run"]
EXPOSE 8097
