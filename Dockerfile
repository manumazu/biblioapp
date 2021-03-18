FROM python:slim

WORKDIR /app

ADD requirements.txt /app
RUN python -m venv venv
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY biblioapp /app/biblioapp
COPY config-init.py /app/config.py
ADD boot.sh /app/
RUN chmod +x /app/boot.sh

ENV FLASK_APP biblioapp

EXPOSE 5000
ENTRYPOINT ["/app/boot.sh"]