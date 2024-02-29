#!/usr/env python3
# -*- coding: UTF-8 -*-

from flask import Flask, request, send_file, make_response
from flask_cors import CORS
import json
import random
import db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})

wordbook = []


def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response


# 开始一盘游戏
@app.route("/start_game", methods=['POST'])
async def start_game():
    """
        开始一盘游戏
    """
    # 输出所有headers参数
    # print(request.headers)
    # 输出headers中的X-Bd-Plugin-Sessionidhash参数
    print("开始一盘游戏")
    session = request.headers.get('X-Bd-Plugin-Sessionidhash')
    print("session: ", session)
    user = db.get_or_create_user(session)
    print("user: ", user)
    board_id = db.create_new_board(user, 8)
    print("board_id: ", board_id)
    board = db.get_board(board_id)
    print("board: ", board)
    return make_json_response({"message": "五子棋游戏开始成功，你为先手，请输入你想下棋的位置。(展示棋盘)",
                               "chessboard": board,
                               "prompt": "首先告知用户五子棋游戏开始成功，用户为先手，再显示棋盘。其中文心一言会返回一个markdown版8x8的表格代表，黑子用O表示，白子用X表示，没有下的位置为-。"})


# 下一步
@app.route("/step", methods=['POST'])
async def next_step():
    """
        下一步
    """
    print("下一步")
    session = request.headers.get('X-Bd-Plugin-Sessionidhash')
    print("session: ", session)
    user = db.get_or_create_user(session)
    print("user: ", user)
    board_id = db.get_board_id(user)
    print("board_id:", board_id)
    board = db.get_board(board_id)
    print("board:", board)
    if not board:
        return make_json_response({"message": "棋盘不存在"})
    x = request.json.get('x', 0)
    y = request.json.get('y', 0)
    # 如果处理成功，返回“处理成功”消息，并且返回当前棋盘，否则返回错误消息
    status, next_board = db.next_step(board_id, user, x, y)
    if next_board is not None:
        return make_json_response({"message": "下一步成功",
                                   "chessboard": next_board,
                                   "prompt": "先回复用户：下一步成功。再返回棋盘。棋盘中：0代表黑子，1代表白子，-代表空，文心一言需要根据这个数组生成markdown版表格8x8棋盘，黑子用O表示，白子用X表示，空仍然为-。"
                                   })
    else:
        return make_json_response({"message": "下一步失败"})


# 结束一盘游戏
@app.route("/end_game", methods=['POST'])
async def end_game():
    """
        结束一盘游戏
    """
    return make_json_response({"message": "五子棋游戏结束成功"})
    # return make_json_response({"message": "游戏结束失败"})


@app.route("/logo.png")
async def plugin_logo():
    """
        注册用的：返回插件的logo，要求48 x 48大小的png文件.
        注意：API路由是固定的，事先约定的。
    """
    return send_file('logo.png', mimetype='image/png')


@app.route("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """
        注册用的：返回插件的描述文件，描述了插件是什么等信息。
        注意：API路由是固定的，事先约定的。
    """
    host = request.host_url
    with open(".well-known/ai-plugin.json", encoding="utf-8") as f:
        text = f.read().replace("PLUGIN_HOST", host)
        return text, 200, {"Content-Type": "application/json"}


@app.route("/.well-known/openapi.yaml")
async def openapi_spec():
    """
        注册用的：返回插件所依赖的插件服务的API接口描述，参照openapi规范编写。
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/openapi.yaml", encoding="utf-8") as f:
        text = f.read()
        return text, 200, {"Content-Type": "text/yaml"}


@app.route('/')
def index():
    return 'welcome to my webpage!'


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8081)
