FROM python:2
WORKDIR /usr/src/app
COPY networkx-1.10 /usr/src/app/networkx-1.10
COPY simpy-2.2  /usr/src/app/simpy-2.2
COPY eon_simulator /usr/src/app/eon_simulator
RUN export PYTHONPATH="${PYTHONPATH}:/usr/src/app/"
RUN python networkx-1.10/setup.py install 
RUN python simpy-2.2/setup.py install 
RUN pip install --no-cache-dir numpy -y
CMD ["eon_simulator/run.py"]
ENTRYPOINT ["python"]
