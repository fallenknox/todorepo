from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import string

app = Flask(__name__)

app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('todo.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS todo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0,
            id_user INTEGER NOT NULL,
            FOREIGN KEY (id_user) REFERENCES user(id)
        )""")
        self.conn.commit()

    def close(self):
        self.conn.close()


db = Database()


@app.route('/')
def index():
    db.cursor.execute("SELECT * FROM user")
    users = db.cursor.fetchall()
    return render_template('index.html', users=users)


@app.route('/users/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        db.cursor.execute("INSERT INTO user (username) VALUES (?)", (username,))
        db.conn.commit()
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/users/delete/<int:id_user>')
def delete_user(id_user):
    db.cursor.execute("DELETE FROM user WHERE id=?", (id_user,))
    db.conn.commit()
    return redirect(url_for('index'))


@app.route('/todo/<int:id_user>')
def todos(id_user):
    db.cursor.execute("SELECT * FROM user WHERE id=?", (id_user,))
    user = db.cursor.fetchone()
    db.cursor.execute("SELECT * FROM todo WHERE id_user=?", (id_user,))
    todos = db.cursor.fetchall()
    return render_template('todo.html', todos=todos, user=user)


@app.route('/add_todo/<int:id>', methods=['GET', 'POST'])
def add_todo_item(id):
    if request.method == 'GET':
        return render_template('add_todo.html', id=id)
    todo = request.form['task']
    db.cursor.execute("INSERT INTO todo (todo, done, id_user) VALUES (?, 0, ?)", (todo, id))
    db.conn.commit()
    return redirect(url_for('todos', id_user=id))


@app.route('/delete_todo/<int:todo_id>')
def delete_todo_item(todo_id):
    db.cursor.execute("SELECT id_user FROM todo WHERE id=?", (todo_id,))
    id_user = db.cursor.fetchone()[0]
    db.cursor.execute("DELETE FROM todo WHERE id=?", (todo_id,))
    db.conn.commit()
    return redirect(url_for('todos', id_user=id_user))


def update_todo_status(todo_id, status):
    db.cursor.execute("SELECT id_user FROM todo WHERE id=?", (todo_id,))
    id_user = db.cursor.fetchone()[0]
    db.cursor.execute("UPDATE todo SET done=? WHERE id=?", (status, todo_id))
    db.conn.commit()
    return redirect(url_for('todos', id_user=id_user))


@app.route('/done/<int:todo_id>')
def mark_done(todo_id):
    return update_todo_status(todo_id, 1)


@app.route('/not_done/<int:todo_id>')
def mark_not_done(todo_id):
    return update_todo_status(todo_id, 0)


@app.route('/edit_todo/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo_item(todo_id):
    if request.method == 'GET':
        db.cursor.execute("SELECT * FROM todo WHERE id=?", (todo_id,))
        todo = db.cursor.fetchone()
        return render_template('edit_todo.html', todo=todo, todo_id=todo[0])

    todo = request.form['task']
    id_user = db.cursor.execute("SELECT id_user FROM todo WHERE id=?", (todo_id,)).fetchone()[0]
    db.cursor.execute("UPDATE todo SET todo=? WHERE id=?", (todo, todo_id))
    db.conn.commit()
    return redirect(url_for('todos', id_user=id_user))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
