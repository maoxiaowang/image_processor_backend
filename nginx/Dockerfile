FROM nginx:1.25

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# install dependencies
RUN rm /etc/apt/sources.list.d/* -f
ADD ./sources.list /etc/apt
RUN apt-get update && apt-get install -y --no-install-recommends netcat iputils-ping
