###########
# BUILDER #
###########

# pull official base image
FROM python:3.10.12-slim-buster as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
ADD ./sources.list /etc/apt
RUN apt-get update && apt-get install -y gcc

# lint
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install flake8==6.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . /usr/src/app/
RUN flake8 --ignore=E501,F401 .

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple


#########
# FINAL #
#########

# pull official base image
FROM python:3.10.12-slim-buster

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/django
RUN mkdir $APP_HOME
RUN bash -c "mkdir -p $APP_HOME/{static,media,data}"
WORKDIR $APP_HOME

# install dependencies
ADD ./sources.list /etc/apt
RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 netcat
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache /wheels/* -i https://pypi.tuna.tsinghua.edu.cn/simple

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

RUN chmod +x  $APP_HOME/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/home/app/django/entrypoint.sh"]
