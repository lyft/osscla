FROM ubuntu:trusty
MAINTAINER Ryan Lane <rlane@lyft.com>

WORKDIR /srv/osscla

RUN apt-get update && \
    apt-get install -y ruby-full npm nodejs nodejs-legacy git git-core && \
    apt-get install -y python python-pip python-dev build-essential libffi-dev

COPY bower.json package.json /srv/osscla/

RUN gem install compass && \
    npm install grunt-cli && \
    npm install

RUN node_modules/grunt-cli/bin/grunt build

COPY piptools_requirements.* requirements.* /srv/osscla
RUN pip install -r piptools_requirements.txt && pip install -r requirements.txt

COPY . /srv/osscla

EXPOSE 80

CMD ["gunicorn","wsgi:app","--workers=2","-k","gevent","--access-logfile=-","--error-logfile=-"]
