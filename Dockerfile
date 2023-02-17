FROM python:slim

#comment if you have already a biblioapp instance in the same directory
COPY . /app
COPY ./config-init.py /app/config.py

WORKDIR /app
RUN ls -l .
RUN python -m pip install --upgrade pip
RUN python -m venv venv
RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV FLASK_APP biblioapp

#run some unit tests to validate app structure
RUN python -m pytest /app/tests/unit

RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["/app/boot.sh"]
