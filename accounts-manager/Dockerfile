FROM python:3.9-rc-alpine

WORKDIR /app

RUN touch /var/log/flat_line.log && chmod 777 /var/log/flat_line.log && \
    touch /var/log/json.log && chmod 777 /var/log/json.log

COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir && rm -f requirements.txt

COPY . .
RUN chmod 777 run.sh && whoami

CMD /app/run.sh