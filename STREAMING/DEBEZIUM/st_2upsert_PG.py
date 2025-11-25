import psycopg2

def update_postgres_data():
    conn = psycopg2.connect(
        dbname="source_db",
        user="user",
        password="password",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()

    # Обновим имена пользователей по id
    updates = [
        (1, "NOVA"),
        (2, "DATA")
    ]
    for user_id, new_name in updates:
        cur.execute("UPDATE public.my_table SET name = %s WHERE id = %s;", (new_name, user_id))

    # Добавим новые записи
    inserts = [
        ("Charlie",),
        ("Diana",)
    ]
    cur.executemany("INSERT INTO public.my_table (name) VALUES (%s);", inserts)

    conn.commit()
    cur.close()
    conn.close()
    print("🔁 Обновления выполнены и новые записи добавлены.")


if __name__ == '__main__':
    update_postgres_data()