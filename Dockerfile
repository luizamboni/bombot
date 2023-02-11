FROM python:3.8

COPY /app /app

WORKDIR /app

# RUN apt update && apt install build-essential
# RUN pip install -U pip setuptools wheel
RUN pip install watchdog

RUN pip install -r requirements.txt

CMD ["watchmedo", "shell-command", '--patterns="*.py"', "--command='python app.py'"]
