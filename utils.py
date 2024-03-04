import requests
import json
import upyun
import uuid

up = upyun.UpYun('yiyan-image', 'yiyanfastapi', 'RNJUsrxw8GE9TqNNFmOXf26BvWk8rGac')


def board_to_image(board):
    url = 'http://47.113.230.250:8000/boardToImage'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        "numbers": board
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    with open('boardToImage.png', 'wb') as f:
        f.write(response.content)
    uuid_str = str(uuid.uuid1())
    # 上传图片到又拍云
    res = up.put(f'/boardToImage/{uuid_str}.png', response.content)
    # print(res)
    img_url = f'https://yiyan-image.mhatp.cn/boardToImage/{uuid_str}.png'
    print(img_url)
    return img_url


# 使用方式：
if __name__ == "__main__":
    board = [["0", "1", "1", "1", "1", "0", "0", "0"], ["0", "0", "0", "0", "0", "0", "0", "0"],
             ["0", "2", "2", "2", "2", "0", "2", "0"], ["0", "0", "0", "0", "0", "0", "0", "0"],
             ["0", "0", "0", "0", "0", "0", "0", "0"], ["0", "0", "0", "0", "0", "0", "0", "0"],
             ["0", "0", "0", "0", "0", "0", "1", "0"], ["0", "0", "0", "0", "0", "0", "0", "0"]]
    image_data = board_to_image(board)
