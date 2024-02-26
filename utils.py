import sqlite3

DATABASE_URL = "chess_test.db"

get_conn = lambda: sqlite3.connect(DATABASE_URL)


def get_conn():
    return sqlite3.connect(DATABASE_URL)


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
            status TEXT -- the status of the board, active, ai_won, user_won, draw
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def create_steps_table():
    """
    id：唯一标识每一步的ID。
    board_id：棋盘ID，用于标识这一步是在哪个棋盘上的。
    step_number：步数。
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
            step_number INTEGER, -- the number of the step
            player TEXT, -- who made the step, user or ai
            x INTEGER, -- the x coordinate of the step
            y INTEGER, -- the y coordinate of the step
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP -- when the step was made
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


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
