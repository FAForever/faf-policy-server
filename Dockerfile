FROM python:3.7
ENV FLASK_APP server/server.py
ENV APP_PORT 8097

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["sh", "-c", "flask run --host=0.0.0.0 --port ${APP_PORT}"]
EXPOSE ${APP_PORT}
