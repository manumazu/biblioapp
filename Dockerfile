FROM python:slim

#comment if you have already a biblioapp instance in the same directory
COPY . /app
COPY ./config-init.py /app/config.py

WORKDIR /app
RUN ls -l .
RUN python -m pip install --upgrade pip
#RUN python -m venv venv
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install flask_wtf --upgrade
RUN pip install flask_login --upgrade

#used for OCR via Vertexai : need the volume "bibliobus-ocr-ia" (see docker-compose)
RUN pip install --upgrade google-cloud-aiplatform gcloud auth login


ENV FLASK_APP biblioapp

#run some unit tests to validate app structure
RUN python -m pytest /app/tests/unit

RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["/app/boot.sh"]
