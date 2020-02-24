import os
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
        <pre>Python调用代码
        values = {
            'rectangles': [
                {
                    'x': 100,
                    'y': 100,
                    'w': 100,
                    'h': 200,
                },
                {
                    'x': 300,
                    'y': 300,
                    'w': 100,
                    'h': 200,
                },
                {
                    'x': 200,
                    'y': 200,
                    'w': 100,
                    'h': 200,
                }
            ]
        }

        filename = 'input.jpg'
        files = {'file': (filename, open(filename, 'rb'), 'image/jpeg', {})}
        response = requests.post(API_URL + "http://localhost:8001/drawing/draw", files=files, data=values, stream=True)
        if response.status_code == 200:
            with open('output.jpg', 'wb+') as f:
                f.write(response.raw.data)
        else:
            print(response.status_code, response.reason)
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
              "paramType": "body"
            },
            {
              "name": "values",
              "description": "绘制的json信息",
              "required": True,
              "allowMultiple": False,
              "dataType": "str",
              "paramType": "body",
              "defaultValue": "\n{\n    'rectangles': [\n        {\n            'x': 100,\n            'y': 100,\n            'w': 100,\n            'h': 200,\n        },\n        {\n            'x': 200,\n            'y': 200,\n            'w': 100,\n            'h': 200,\n        },\n    ]\n}"
            }
          ],
        consumes=[
            "multipart/form-data"
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
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()

        img_file = args.file
        if not img_file:
            app.logger.info('file no setting')
            return 'no file', 417

        rectangles = []
        for rectangle_str in request.values.getlist('rectangles'):
            rectangle = eval(rectangle_str)
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