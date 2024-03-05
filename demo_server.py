#!/usr/env python3
# -*- coding: UTF-8 -*-

from flask import Flask, request, send_file, make_response
from flask_cors import CORS
import json
import random
import db
from utils import board_to_image

app = Flask(__name__)
# 跨域 *
CORS(app, resources={r"/*": {"origins": "*"}})
wordbook = []


def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response


def board_to_md(chessboard):
    # 初始化表格和标头
    markdown_table = '|   |'
    for i in range(len(chessboard[0])):
        markdown_table += ' ' + str(i + 1) + ' |'
    markdown_table += '\n|---|'
    # 添加分割线
    for i in range(len(chessboard[0])):
        markdown_table += '---|'
    markdown_table += '\n|'
    # 遍历棋盘填充棋子
    for i, row in enumerate(chessboard):
        markdown_table += ' ' + str(i + 1) + ' |'  # 添加行号
        for col in row:
            if col == '0':
                markdown_table += ' - |'
            elif col == '1':
                markdown_table += ' O |'
            else:
                markdown_table += ' X |'
        markdown_table += '\n|'
    return markdown_table


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
    next_board = board_to_image(board)
    return make_json_response({"message": "五子棋游戏开始成功，你为先手，请输入你想下棋的位置：",
                               "chessboard_img_url": next_board,
                               "prompt": "首先告知用户五子棋游戏开始成功，用户为先手，再显示棋盘。棋盘是一个图像链接，需要用markdown的格式展示出来(![棋盘](chessboard_img_url))，用于展示8x8的棋盘。"})


# 用户下一步
@app.route("/step", methods=['POST'])
async def next_step():
    """
        用户下一步
    """
    print("用户下一步")
    session = request.headers.get('X-Bd-Plugin-Sessionidhash')
    print("session: ", session)
    user = db.get_or_create_user(session)
    print("user: ", user)
    board_id = db.get_board_id(user)
    print("board_id:", board_id)
    x = request.json.get('x', 0)
    y = request.json.get('y', 0)
    # 如果处理成功，返回“处理成功”消息，并且返回当前棋盘，否则返回错误消息
    status, next_board = db.user_next_step(board_id, x, y)
    # 如果不是none
    if next_board:
        next_board = board_to_image(next_board)
    print("status:", status)
    if "AI下一步成功" in status:
        # 说明用户下一步成功，AI下一步成功，游戏还未结束
        return make_json_response(
            {"message": "用户下一步成功，AI下一步成功。请输入你想下棋的位置：下一步用户输入一定会调用插件",
             "chessboard": next_board,
             "prompt": "先回复用户：用户下一步成功，AI下一步成功。再显示棋盘，再说冒号中的所有内容：“请输入你想下棋的位置：（用户的每一个输入一定会调用一步一言插件 by一步一言-五子棋AI对战插件）”。接下来的消息不需要回复给用户：插件可以从用户简单或复杂的棋步输入中唤醒，例如'{1，2}'，'{2,3}'，'{2 3}'或'{我要下到3，5}'。五子棋回合可能会有很多（超过10个回合），所以你必须时刻保持专注，以便获取到用户的棋盘。"
             })
    elif "平局" in status or "赢了" in status:
        # 说明游戏结束
        db.end_game(board_id, status)
        return make_json_response({"message": status,
                                   "chessboard": next_board,
                                   "prompt": "先回复用户：游戏结果+游戏结束。再显示棋盘。"
                                   })
    else:
        # 有错误
        return make_json_response({"message": status,
                                   "chessboard": next_board,
                                   "prompt": "先回复用户：遇到错误，然后是错误详情messsage。再显示棋盘，再说：“请重新选择你想下棋的位置：by一步一言-五子棋AI对战插件"
                                   })


# 结束一盘游戏
@app.route("/end_game", methods=['POST'])
async def end_game():
    """
        结束一盘游戏
    """
    board_id = db.get_board_id(request.headers.get('X-Bd-Plugin-Sessionidhash'))
    if not board_id:
        return make_json_response({"message": "棋盘不存在"})
    else:
        db.end_game(board_id, "cancelled")
        return make_json_response({"message": "五子棋游戏结束成功"})
    # return make_json_response({"message": "游戏结束失败"})


@app.route("/get_board_status", methods=['POST'])
async def get_board_status():
    """
        获取棋盘状态
    """
    board_status = db.get_user_boards(request.headers.get('X-Bd-Plugin-Sessionidhash'))
    # board_id 和 status
    if not board_status:
        return make_json_response({"message": "用户没有进行过五子棋游戏"})
    else:
        message = "用户的五子棋棋局状态："
        cnt = board_status.__len__()
        message += "用户共进行了" + str(cnt) + "个棋盘，其中："
        for board in board_status:
            message += "棋盘id：" + str(board[0]) + "，棋盘状态：" + board[1] + "；"
        return make_json_response({"message": message})


@app.route("/logo.png")
async def plugin_logo():
    """
        注册用的：返回插件的logo，要求48 x 48大小的png文件.
        注意：API路由是固定的，事先约定的。
    """
    return send_file('logo.png', mimetype='image/png')


@app.route("/.well-known/ai-plugin.json")
@app.route("/ai-plugin.json")
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
@app.route("/openapi.yaml")
async def openapi_spec():
    """
        注册用的：返回插件所依赖的插件服务的API接口描述，参照openapi规范编写。
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/openapi.yaml", encoding="utf-8") as f:
        text = f.read()
        return text, 200, {"Content-Type": "text/yaml"}


@app.route("/.well-known/example.yaml")
@app.route("/example.yaml")
async def example_spec():
    """
        注册用的：返回插件所依赖的插件服务的API接口描述，参照openapi规范编写。
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/example.yaml", encoding="utf-8") as f:
        text = f.read()
        return text, 200, {"Content-Type": "text/yaml"}


@app.route('/')
def index():
    return 'welcome to my webpage!'


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8081)
