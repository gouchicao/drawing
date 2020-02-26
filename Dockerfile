FROM ubuntu:18.04
LABEL maintainer="wang-junjian@qq.com"

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nano \
    && rm -rf /var/lib/apt/lists/*

ENV PROJECT_PATH /drawing/

ADD requirements.txt $PROJECT_PATH
WORKDIR $PROJECT_PATH
RUN pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ADD . $PROJECT_PATH

EXPOSE 8001

CMD ["gunicorn", "main:app", "-b 0.0.0.0:8001"]
#ENTRYPOINT ["gunicorn", "main:app", "-b 0.0.0.0:8001"]
