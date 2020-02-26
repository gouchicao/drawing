FROM python:alpine
LABEL maintainer="wang-junjian@qq.com"

# 修改源
RUN echo "http://mirrors.aliyun.com/alpine/v3.11/main/" > /etc/apk/repositories && \
    echo "http://mirrors.aliyun.com/alpine/v3.11/community/" >> /etc/apk/repositories

# pillow 依赖
RUN apk update \
    && apk add --no-cache build-base jpeg-dev zlib-dev

ENV PROJECT_PATH /drawing/

ADD requirements.txt $PROJECT_PATH
WORKDIR $PROJECT_PATH
RUN pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ADD . $PROJECT_PATH

EXPOSE 8001

ENTRYPOINT ["python3", "main.py"]
