# drawing 绘制服务

## 构建镜像
``` bash
sudo docker build -t gouchicao/drawing:latest .
```

## 运行容器
``` bash
sudo docker run --rm -it --name=drawing -p 8001:8001 gouchicao/drawing:latest
```

## 访问开发文档
```
打开浏览器，输入：127.0.0.1:8001/docs
```

## 服务地址
```
http://127.0.0.1:8001/drawing/draw
```
