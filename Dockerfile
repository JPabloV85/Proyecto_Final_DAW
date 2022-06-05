FROM python:3.9
RUN pip3 install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000
ENTRYPOINT [ "flask" ]
CMD [ "run", "--host=0.0.0.0" ]