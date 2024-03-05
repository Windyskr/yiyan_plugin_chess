import requests
import json
import upyun

up = upyun.UpYun('yiyan-image', 'yiyanfastapi', 'RNJUsrxw8GE9TqNNFmOXf26BvWk8rGac')


def board_to_hex(board):
    def base3_to_decimal(b3):
        return int(''.join(str(i) for i in b3), 3)

    # 用于存储棋盘三进制表示
    base3_board = []

    # 遍历棋盘，按顺序将状态添加到三进制列表中
    for row in board:
        for cell in row:
            base3_board.append(str(cell))

    # 将三进制列表转换为十进制数
    decimal_representation = base3_to_decimal(base3_board)

    # 将十进制数转换为十六进制数，并移除前面的 "0x"
    hex_representation = hex(decimal_representation)[2:]
    print(hex_representation)
    return str(hex_representation)


def board_to_image(board):
    board_hex = board_to_hex(board)
    img_url = f'https://yiyan-image.mhatp.cn/boardToImage/{board_hex}.png'
    get_response = requests.get(img_url)
    if get_response.status_code == 200:
        print("图片已经存在 " + img_url)
        return img_url
    else:
        url = 'http://47.113.230.250:8000/boardToImage'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = {
            "numbers": board
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        img_url = f'https://yiyan-image.mhatp.cn/boardToImage/{board_hex}.png!yiyan'
        print("图片正在上传：" + img_url)
        res = up.put(f'/boardToImage/{board_hex}.png', response.content, checksum=True)
        return img_url


# 使用方式：
if __name__ == "__main__":
    board = [['1', '2', '1', '1', '2', '1', '1', '2'], ['2', '1', '1', '2', '0', '0', '0', '0'],
             ['0', '0', '0', '1', '2', '0', '0', '0'], ['0', '0', '0', '0', '2', '0', '0', '0'],
             ['0', '0', '0', '2', '1', '2', '0', '0'], ['0', '0', '0', '0', '1', '2', '0', '0'],
             ['0', '0', '0', '0', '0', '0', '0', '0'], ['0', '0', '0', '0', '0', '0', '0', '0']]
    image_data = board_to_image(board)
