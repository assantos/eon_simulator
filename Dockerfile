FROM python:2

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

ENTRYPOINT ["python", "run.py"]
