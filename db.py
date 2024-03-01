import sqlite3
import json
import requests

DATABASE_URL = "chess_test.db"

get_conn = lambda: sqlite3.connect(DATABASE_URL)


def create_user_table():
    """
    id: 用户的唯一标识。
    session_id: 用户的会话ID。
    created_at: 用户的创建时间。
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        -- This table stores the users
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- unique identifier for each user
            session_id TEXT, -- the session id of the user
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- when the user was created
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def create_boards_table():
    """
    id：唯一标识每个棋盘的ID。
    user_id：用户ID，用于标识哪个用户的棋盘。
    created_at：棋盘创建的时间。
    updated_at：棋盘最后一次更新的时间。
    status：棋盘的状态，active表示正在进行中，ai_won表示AI赢了，user_won表示用户赢了，draw表示平局。
    board：棋盘的字符串表示。
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        -- This table stores the chess boards
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- unique identifier for each board
            user_id INTEGER, -- identifier for the user
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- when the board was created
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- when the board was last updated
            status TEXT, -- the status of the board, active, ai_won, user_won, draw
            board TEXT -- the string representation of the board
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def create_steps_table():
    """
    id：唯一标识每一步的ID。
    board_id：棋盘ID，用于标识这一步是在哪个棋盘上的。
    player：谁走的这一步，例如"user"表示用户走的，"ai"表示AI走的。
    x：棋子的x坐标。
    y：棋子的y坐标。
    timestamp：这一步的时间。
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        -- This table stores the steps of the chess game
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- unique identifier for each step
            board_id INTEGER, -- identifier for the chess board
            player TEXT, -- who made the step, user or ai
            x INTEGER, -- the x coordinate of the step
            y INTEGER, -- the y coordinate of the step
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP -- when the step was made
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# 查询用户id，如果没有则插入
def get_or_create_user(session_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE session_id=?", (session_id,))
    user = cursor.fetchone()
    if user:
        user_id = user[0]
    else:
        cursor.execute("INSERT INTO users (session_id) VALUES (?)", (session_id,))
        conn.commit()
        user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


# 查询用户棋盘id
def get_board_id(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM boards WHERE user_id=? AND status='active'", (user_id,))
    board = cursor.fetchone()
    print(board)
    cursor.close()
    conn.close()
    if board:
        return board[0]
    return None


# 创建一个新的棋盘，返回棋盘id
# 棋盘大小由用户指定
def create_new_board(user_id, board_size):
    # 棋盘是一个二维数组，用字符串表示
    board = [["0" for _ in range(board_size)] for _ in range(board_size)]
    board_str = "\n".join(["".join(row) for row in board])
    status = "active"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO boards (user_id, board, status) VALUES (?, ?, ?)", (user_id, board_str, status))
    conn.commit()
    board_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return board_id


def end_game(board_id, status):
    print("db end_game", board_id, status)
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE boards SET status=? WHERE id=?", (status, board_id))
    conn.commit()
    cursor.close()
    conn.close()
    print("db end_game done")


# 获取棋盘的数组
# 如果棋盘不存在，返回"棋盘不存在"
def get_board(board_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT board FROM boards WHERE id=?", (board_id,))
    board_str_tuple = cursor.fetchone()
    cursor.close()
    conn.close()
    if not board_str_tuple:
        return None
    board_str = board_str_tuple[0]
    return [list(row) for row in board_str.split("\n")]


# 判断现在下棋的用户是否合法
# 如果现在轮到的用户不是指定的用户，返回false
# 如果是第一轮，返回True
# 如果合法，返回True
def check_player(board_id, player):
    print("db check_player", board_id, player)
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT player FROM steps WHERE board_id=? ORDER BY id DESC LIMIT 1", (board_id,))
    last_player = cursor.fetchone()
    cursor.close()
    conn.close()
    if not last_player:
        print("第一轮")
        return True
    else:
        print("last_player", last_player[0])
        return last_player[0] != player


# 下一步，需要指定棋盘id，下棋的玩家，以及下棋的位置
# 首先检查棋盘是否存在，然后检查是否轮到这个玩家下棋，然后检查这个位置是否合法
# 如果一切正常，就在这个位置下棋
def next_step(board_id, player, x, y):
    # player: user or AI
    print("db next_step", board_id, player, x, y)
    board = get_board(board_id)
    if not board:
        print("error棋盘不存在")
        return "error棋盘不存在", None
    if x <= 0 or x > len(board) or y <= 0 or y > len(board[0]):
        print("error越界了")
        return "error越界了", None
    if board[x - 1][y - 1] != "0":
        print("error这个位置已经有棋子了")
        return "error这个位置已经有棋子了", None
    # 是否轮到这个玩家下棋
    if not check_player(board_id, player):
        print("error现在不是你下棋的时候")
        return "error现在不是你下棋的时候", None
    conn = get_conn()
    cursor = conn.cursor()
    # 在这个位置下棋，更新棋盘和步数
    # user下的是1，ai下的是2，0是空
    board[x - 1][y - 1] = player == "user" and "1" or "2"
    board_str = "\n".join(["".join(row) for row in board])
    cursor.execute("INSERT INTO steps (board_id, player, x, y) VALUES (?, ?, ?, ?)",
                   (board_id, player, x, y))
    cursor.execute("UPDATE boards SET board=? WHERE id=?", (board_str, board_id))
    conn.commit()
    cursor.close()
    conn.close()
    current_winner = ai_check(board_id)
    board_show = get_board(board_id)
    if current_winner == "ai_won":
        print("AI赢了", board_show)
        return "AI赢了", board_show
    elif current_winner == "user_won":
        print("用户赢了", board_show)
        return "用户赢了", board_show
    elif current_winner == "draw":
        print("平局", board_show)
        return "平局", board_show

    if player == "user":
        print("用户下一步成功", board_show)
        return "用户下一步成功", board_show
    else:
        print("AI下一步成功", board_show)
        return "AI下一步成功", board_show


# 用户下一步
def user_next_step(board_id, x, y):
    print("db user_next_step", board_id, x, y)
    status, board_str = next_step(board_id, "user", x, y)
    if status == "用户下一步成功":
        return ai_next_step(board_id)
    else:
        return status, board_str


# AI下一步
baseurl = "https://wzqai.mhatp.cn"


def ai_next_step(board_id):
    print("db ai_next_step", board_id)
    board = get_board(board_id)
    print("board", board)
    if not board:
        return "error棋盘不存在"
    # 请求 /next 接口
    # url = baseurl + "/next"
    # headers = {'Content-Type': 'application/json'}
    # data = {"board": board}
    # response = requests.post(url, headers=headers, data=json.dumps(data))
    # if response.status_code != 200:
    #     return "errorAI下一步失败"
    # status = response.json().get("status")
    # next_step = response.json().get("next_step")
    # print("status", status, "next_step", next_step)
    # x = next_step[0][0], y = next_step[0][1]
    x = 5
    y = 7
    return next_step(board_id, "ai", x, y)


def ai_check(board_id):
    print("db ai_check", board_id)
    board = get_board(board_id)
    print("board", board)
    if not board:
        return "棋盘不存在"
    # 请求 /check 接口
    url = baseurl + "/check"
    headers = {'Content-Type': 'application/json'}
    data = {"board": board}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        return "errorAI检查失败"
    status = response.json().get("status")
    print("AI check status", status)
    return status


if __name__ == "__main__":
    # 删除原有的数据库
    import os

    if os.path.exists(DATABASE_URL):
        os.remove(DATABASE_URL)
    # 创建新的数据库
    create_user_table()
    create_boards_table()
    create_steps_table()
    print("数据库初始化成功")
