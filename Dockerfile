FROM python:3.7
ENV FLASK_APP server/server.py
ENV APP_PORT 8097

COPY . /app
WORKDIR /app

RUN pip install pipenv
RUN pipenv install

CMD ["sh", "-c", "pipenv run server"]
EXPOSE ${APP_PORT}
