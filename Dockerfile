FROM python:3.9
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 5000
ENTRYPOINT [ "flask"]
CMD [ "run", "--host", "0.0.0.0" ]