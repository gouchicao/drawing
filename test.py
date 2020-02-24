import os
import requests
import json


API_URL = 'http://127.0.0.1:8001/'
MAX_RETRIES = 60


def draw(filename):
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

    files = {'file': (filename, open(filename, 'rb'), 'image/jpeg', {})}
    response = requests.post(API_URL + "drawing/draw", files=files, data=values, stream=True)
    if response.status_code == 200:
        with open('output.jpg', 'wb+') as f:
            f.write(response.raw.data)
    else:
        print(response.status_code, response.reason)


if __name__ == '__main__':
    draw('input.jpg')
    