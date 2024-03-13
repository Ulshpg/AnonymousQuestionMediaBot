import aiosqlite, asyncio
from typing import Literal


PATH_TO_DB = "user_database.db"
# Функция для создания базы данных
async def create_database():
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.cursor()
        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            ID INTEGER UNIQUE,
            NAME TEXT,
            USERNAME TEXT,
            RECEIVED INTEGER, 
            SENT INTEGER,
            TRANSITIONS INTEGER
        )
        ''')
        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS vip (
            ID INTEGER UNIQUE
        )
        ''')
        await db.commit()

# Функция для вставки данных по ID во второй и третий столбцы или для добавления нового пользователя
async def insert_data(id, name, username):
    try:
        async with aiosqlite.connect(PATH_TO_DB) as db:
            cursor = await db.cursor()
            
            # Проверяем, существует ли пользователь с указанным ID
            await cursor.execute('SELECT * FROM users WHERE ID = ?', (id,))
            result = await cursor.fetchone()
            if result:
                # Пользователь существует, обновляем только NAME и USERNAME
                await cursor.execute("UPDATE users SET NAME = ?, USERNAME = ? WHERE ID = ?", (name, username, id))
            else:
                # Пользователь не существует, вставляем новую запись
                await cursor.execute("INSERT INTO users (ID, NAME, USERNAME, RECEIVED, SENT, TRANSITIONS) VALUES (?, ?, ?, 0, 0, 0)", (id, name, username))
            
            await db.commit()

    except Exception as e:
        print(f"Ошибка при вставке/обновлении данных пользователя: {e}")


# Функция для получения имени и ника по ID
async def get_names(id):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT NAME, USERNAME FROM users WHERE ID = ?', (id,))
        result = await cursor.fetchone()
    return result

async def get_stats(id):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT RECEIVED, SENT, TRANSITIONS FROM users WHERE ID = ?', (id,))
        result = await cursor.fetchone()
    return result

async def get_username_by_id(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT USERNAME FROM users WHERE ID = ?", (user_id,))
        username = await cursor.fetchone()
        if username:
            return username[0]  # Возвращает значение USERNAME
        else:
            return "Отсутствует"  # Если пользователь с указанным ID не найден, возвращает None

async def get_all_vips():
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT ID FROM vip')
        ids = [row[0] for row in await cursor.fetchall()]
    return ids

async def check_user_exists(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE ID = ?", (user_id,))
        result = await cursor.fetchone()
        return result[0] > 0

async def add_vip(id, second):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.cursor()
        await cursor.execute('REPLACE INTO vip (ID, DATAEND) VALUES (?, ?)', (id, second))
        await db.commit()
    return await get_all_vips()

async def get_vip_data_by_id(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.execute("SELECT DATAEND FROM vip WHERE ID = ?", (user_id,))
        result = await cursor.fetchone()
        if result:
            return result[0]  # Возвращает значение из столбца seconds для указанного ID
        else:
            return None  # Если пользователь с указанным ID не найден

async def delete_vip_by_id(id):
    try:
        async with aiosqlite.connect(PATH_TO_DB) as db:
            cursor = await db.cursor()
            await cursor.execute('DELETE FROM vip WHERE ID = ?', (id,))
            await db.commit()
            await cursor.close()
        print(f"Запись с id {id} успешно удалена из таблицы vip.")
        return await get_all_vips()
    except Exception as e:
        print(f"Ошибка при удалении записи из таблицы vip: {e}")

async def increment_field_by_id(user_id, field: Literal["RECEIVED", "SENT", "TRANSITIONS"]):
    async with aiosqlite.connect(PATH_TO_DB) as db:
        cursor = await db.execute(f"UPDATE users SET {field} = {field} + 1 WHERE ID = ?", (user_id,))
        await db.commit()
        return cursor.rowcount > 0

# async def get_all_id():
#     async with aiosqlite.connect(PATH_TO_DB) as db:
#         cursor = await db.cursor()
#         await cursor.execute('SELECT ID FROM users')
#         ids = [row[0] for row in await cursor.fetchall()]
#     return ids

# async def update_table_to_zero():
#     async with aiosqlite.connect(PATH_TO_DB) as db:
#         cursor = await db.cursor()
#         await cursor.execute(f'UPDATE users SET INP = 0, OUTP = 0')
#         await db.commit()

# async def get_value_count(column: str, user_id):
#     async with aiosqlite.connect("user_database.db") as db:
#         cursor = await db.cursor()
#         await cursor.execute(f"SELECT {column} FROM users WHERE ID = ?", (user_id,))
#         current_value = await cursor.fetchone()
#         return current_value[0]

# async def changing_count_messages(column, user_id):
#     async with aiosqlite.connect("user_database.db") as db:
#         cursor = await db.cursor()
#         current_value = await get_value_count(column, user_id)
#         if current_value:
#             new_value = current_value + 1
#             await cursor.execute(f'UPDATE users SET {column} = ? WHERE ID = ?', (new_value, user_id))
#             await db.commit()

# print(asyncio.run(changing_count_messages("OUTP", 6504205024)))