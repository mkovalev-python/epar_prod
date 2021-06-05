# pull official base image
FROM python:2.7

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN npm install -g cssmin uglify-js

COPY ./entrypoint.sh .
RUN sed -i 's/\r//' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# copy project
COPY . .

ENTRYPOINT ["sh","/usr/src/app/entrypoint.sh"]

