from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# DB INIT
def init_db():
    conn = sqlite3.connect('task.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = sqlite3.connect('task.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username,password) VALUES (?,?)",
                    (request.form['username'], request.form['password']))

        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('register.html')


# LOGIN
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('task.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (request.form['username'], request.form['password']))

        user = cur.fetchone()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template('login.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    conn = sqlite3.connect('task.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks WHERE user_id=?",
                (session['user_id'],))

    tasks = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', tasks=tasks)


# ADD TASK
@app.route('/add', methods=['POST'])
def add():
    conn = sqlite3.connect('task.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO tasks (user_id,title) VALUES (?,?)",
                (session['user_id'], request.form['task']))

    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/view')
def view():
    if 'user_id' not in session:
        return redirect('/')

    conn = sqlite3.connect('task.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks WHERE user_id=?",
                (session['user_id'],))

    tasks = cur.fetchall()
    conn.close()

    return render_template('view.html', tasks=tasks)


# DELETE TASK
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('task.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    conn = sqlite3.connect('task.db')
    cur = conn.cursor()

    if request.method == 'POST':
        new_task = request.form['task']

        cur.execute("UPDATE tasks SET title=? WHERE id=?",
                    (new_task, id))

        conn.commit()
        conn.close()
        return redirect('/dashboard')

    # GET → fetch old data
    cur.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()
    conn.close()

    return render_template('edit.html', task=task)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

app.run(debug=True)