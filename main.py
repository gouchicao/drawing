import os
import json
import logging
import tempfile

import werkzeug
from flask import Flask, request, jsonify, make_response, redirect, url_for, send_file
#conda install -c conda-forge flask-restful
from flask_restful import reqparse, abort, Api, Resource
from flask_restful_swagger import swagger

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

"""
sudo docker build -t gouchicao/drawing:latest .
sudo docker run --rm -it --name=drawing -p 8001:8001 gouchicao/drawing:latest
sudo docker push gouchicao/drawing:latest
"""

app = Flask(__name__, static_folder='static')
api = swagger.docs(Api(app), apiVersion='1.0',
                   description='A Drawing API')

file_handler = logging.FileHandler('app.log')
app.logger.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(file_handler)


class Drawing(object):

    def __init__(self, img):
        self.draw = ImageDraw.Draw(img)

    def get_font(self, font_size):
        font_path = 'fonts/NotoSansCJK-Medium.ttc'
        return ImageFont.truetype(font_path, font_size, encoding="unic")

    def rectangle(self, xy, color='red', width=4):
        self.draw.rectangle(xy, outline=color, width=width)

    def text(self, xy, text, color='black', fontsize=12):
        self.draw.text(xy, text, fill=color, font=self.get_font(fontsize))


class Draw(Resource):
    """
    绘制服务
    """

    @swagger.operation(
        notes="""输入图片及要绘制的json信息，输出绘制后的图片。
        <pre>Python 调用例子
            import os
            import requests
            import json


            API_URL = 'http://127.0.0.1:8001/'
            MAX_RETRIES = 60


            def draw(filename):
                values = {
                    "rectangles": [
                        {
                            "x": 100,
                            "y": 100,
                            "w": 100,
                            "h": 200
                        },
                        {
                            "x": 300,
                            "y": 300,
                            "w": 100,
                            "h": 200
                        },
                        {
                            "x": 200,
                            "y": 200,
                            "w": 100,
                            "h": 200
                        }
                    ]
                }

                files = {'file': (filename, open(filename, 'rb'), 'image/jpeg', {})}
                json_str = json.dumps(values)
                response = requests.post(API_URL + "drawing/draw", files=files, data={"json": json_str}, stream=True)
                if response.status_code == 200:
                    with open('output.jpg', 'wb+') as f:
                        f.write(response.raw.data)
                else:
                    print(response.status_code, response.reason)


            if __name__ == '__main__':
                draw('input.jpg')
        </pre>

        <pre>Java-Unirest 调用例子
            Unirest.setTimeouts(0, 0);
            HttpResponse<String> response = Unirest.post("http://127.0.0.1:8001/drawing/draw")
            .header("Content-Type", "multipart/form-data")
            .field("file", new File("input.jpg"))
            .field("json", "{
                \"rectangles\": [
                    {
                        \"x\": 100,
                        \"y\": 100,
                        \"w\": 100,
                        \"h\": 200
                    },
                    {
                        \"x\": 300,
                        \"y\": 300,
                        \"w\": 100,
                        \"h\": 200
                    },
                    {
                        \"x\": 200,
                        \"y\": 200,
                        \"w\": 100,
                        \"h\": 200
                    }
                ]
            }")
            .asString();
        </pre>

        <pre>Java-OkHttp 调用例子
            OkHttpClient client = new OkHttpClient().newBuilder()
            .build();
            MediaType mediaType = MediaType.parse("multipart/form-data");
            RequestBody body = new MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart("file","input.jpg",
                RequestBody.create(MediaType.parse("application/octet-stream"),
                new File("input.jpg")))
            .addFormDataPart("json", "{
                \"rectangles\": [
                    {
                        \"x\": 100,
                        \"y\": 100,
                        \"w\": 100,
                        \"h\": 200
                    },
                    {
                        \"x\": 300,
                        \"y\": 300,
                        \"w\": 100,
                        \"h\": 200
                    },
                    {
                        \"x\": 200,
                        \"y\": 200,
                        \"w\": 100,
                        \"h\": 200
                    }
                ]
            }")
            .build();
            Request request = new Request.Builder()
            .url("http://127.0.0.1:8001/drawing/draw")
            .method("POST", body)
            .addHeader("Content-Type", "multipart/form-data")
            .build();
            Response response = client.newCall(request).execute();
        </pre>
        """,
        nickname='draw',
        parameters=[
            {
              "name": "file",
              "description": "图片文件",
              "required": True,
              "allowMultiple": False,
              "dataType": "file",
              "paramType": "form"
            },
            {
              "name": "json",
              "description": "绘制的json信息",
              "required": True,
              "allowMultiple": False,
              "dataType": "str",
              "paramType": "form",
              "defaultValue": '\n{\n    "rectangles": [\n        {\n            "x": 100,\n            "y": 100,\n            "w": 100,\n            "h": 200\n        },\n        {\n            "x": 200,\n            "y": 200,\n            "w": 100,\n            "h": 200\n        }\n    ]\n}'
            }
          ],
        responseMessages=[
            {
              "code": 200,
              "reason": "输出绘制后的图片"
            },
            {
              "code": 417,
              "reason": "no file"
            },
            {
              "code": 418,
              "reason": "draw failed"
            }
          ]
        )
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True)
        parse.add_argument('json', type=str)
        args = parse.parse_args()

        img_file = args.file
        if not img_file:
            app.logger.info('file no setting')
            return 'no file', 417

        rectangles = []
        if args.json:
            json_obj = json.loads(args.json)
            for rectangle in json_obj['rectangles']:
                rectangles.append(((rectangle['x'], rectangle['y']), 
                                (rectangle['x']+rectangle['w'], rectangle['y']+rectangle['h'])))

        img = None
        with tempfile.NamedTemporaryFile() as temp_file:
            img_data = img_file.read()
            temp_file.write(img_data)

            try:
                img = Image.open(temp_file)
            except:
                app.logger.info('cannot identify image file.')
                abort(401)

            drawing = Drawing(img)
            for rectangle in rectangles:
                drawing.rectangle(rectangle)
            # drawing.text((100, 350), 'open', fontsize=30)

            img.save(temp_file.name, 'JPEG', optimize=True)
            return send_file(temp_file.name, mimetype='image/jpeg')

        app.logger.info('draw failed')
        return 'draw failed', 418


api.add_resource(Draw, '/drawing/draw')


@app.route('/docs')
def docs():
  return redirect('/static/docs.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001, debug=True)