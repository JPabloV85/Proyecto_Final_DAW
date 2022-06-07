# Get base image and upgrade pip
FROM python:3.9-slim-buster
RUN pip3 install --upgrade pip

WORKDIR /app

# Install api requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy api files
COPY . .

# Expose pot and run api
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]