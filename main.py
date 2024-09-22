from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   make_response,
                   flash,
                   session)
import hashlib
from datetime import datetime, date
import random, string
from config import conn, cursor

app = Flask(__name__)

@app.route('/')
def index():
    username = request.cookies.get('username') if request.cookies else None

    if request.cookies:
        return redirect(url_for('home'))

    if username != None:
        return render_template('home.html')
    else:
        return render_template('index.html',
                                action = '/profile' if username != None else '/login'
                            )

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/log', methods=['POST', 'GET'])
def log():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        md5 = hashlib.md5(password.encode()).hexdigest()

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, md5,))
        is_exists = cursor.fetchall()

        if len(is_exists) > 0:
            resp = make_response(redirect(url_for('profile')))
            resp.set_cookie('username', username, max_age=2592000)
            return resp
        else:
            return render_template('login.html', error='Неправильний логін чи пароль')
        
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        is_exists = cursor.fetchall()

        if len(is_exists) > 0:
            return render_template('register.html', error='exists')

        if len(username) == 0 or len(password) == 0 or len(password2) == 0:
            return render_template('register.html', error='Введи усі дані')
        elif len(username) < 5 or len(username) > 20:
            return render_template('register.html', error='Ім\'я користувача від 5 до 20 символів')
        elif len(password) < 8 or len(password) > 20:
            return render_template('register.html', error='Пароль від 8 до 20 символів')
        elif password != password2:
            return render_template('register.html', error='Паролі не збігаються')
        else:
            md5 = hashlib.md5(password.encode()).hexdigest()

            current_date = datetime.now()
            date = current_date.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("INSERT INTO users (username, password, date) VALUES (%s, %s, %s)", (username, md5, date))
            conn.commit()
            resp = make_response(redirect(url_for('profile')))
            resp.set_cookie('username', username, max_age=2592000)
            return resp

@app.route('/profile')
def profile():
    username = request.cookies.get('username') if request.cookies else None

    letter = username[:1].upper()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username))
    user_data = cursor.fetchall()

    cursor.execute("SELECT * FROM habbits WHERE author = %s", (username))
    user_habbits = cursor.fetchall()

    cursor.execute("SELECT * FROM active WHERE author = %s OR mate != ''", (username))
    user_actives = cursor.fetchall()

    current_date = date.today()
    current_day = current_date.day

    last_day = user_actives[0][7] if user_actives else ...
    days = user_actives[0][6] if user_actives else ...
    goal = user_actives[0][5] if user_actives else ...

    # procent = round(((days / goal) * 100), 1) if user_actives else ...

    return render_template('profile.html',
                           username=username,
                           user_data=user_data,
                           letter=letter,
                           city=user_data[0][4],
                           about=user_data[0][5],
                           habbits_count=len(user_habbits),
                           user_actives=user_actives,
                           current_day=str(current_day),
                           last_day=str(last_day),
                        #    procent=procent
                           )

@app.route('/city', methods=['POST', 'GET'])
def city():
    username = request.cookies.get('username')
    city = request.form.get('city')

    cursor.execute("UPDATE users SET city = %s WHERE username = %s", (city, username))
    cursor.execute("UPDATE habbits SET city = %s WHERE author = %s", (city, username))
    conn.commit()

    return make_response(redirect(url_for('profile')))

@app.route('/about', methods=['POST', 'GET'])
def about():
    username = request.cookies.get('username')
    about = request.form.get('about')

    cursor.execute("UPDATE users SET about = %s WHERE username = %s", (about, username))
    conn.commit()

    return make_response(redirect(url_for('profile')))

@app.route('/home', methods=['POST', 'GET'])
def home():
    username = request.cookies.get('username')

    cursor.execute("SELECT * FROM habbits WHERE author != %s AND active = %s AND mate = '' ORDER BY date DESC", (username, '+'))
    habbits_list = cursor.fetchall()

    return render_template('home.html',
                            habbits_list=habbits_list
                           )

@app.route('/create', methods=['POST', 'GET'])
def create():
    username = request.cookies.get('username')

    title = request.form.get('title')
    description = request.form.get('description')
    goal = request.form.get('goal')

    characters = string.ascii_letters + string.digits
    q = ''.join(random.choice(characters) for _ in range(5))

    current_date = datetime.now()
    date = current_date.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("SELECT city FROM users WHERE username = %s", (username))
    city = cursor.fetchall()[0][0]

    cursor.execute("INSERT INTO habbits (q, author, title, description, goal, date, city) VALUES (%s, %s, %s, %s, %s, %s, %s)", (q, username, title, description, goal, date, city))
    conn.commit()

    return make_response(redirect(url_for('list_')))

@app.route('/list', methods=['POST', 'GET'])
def list_():
    username = request.cookies.get('username')

    cursor.execute("SELECT * FROM habbits WHERE author = %s ORDER BY date DESC", (username))
    user_habbits = cursor.fetchall()

    return render_template('list.html',
                           user_habbits=user_habbits
                           )

@app.route('/list-connected', methods=['POST', 'GET'])
def list_connected():
    username = request.cookies.get('username')

    cursor.execute("SELECT * FROM active WHERE mate = %s", (username))
    user_active = cursor.fetchall()

    if user_active:
        q = user_active[0][1]

        cursor.execute("SELECT * FROM habbits WHERE q = %s ORDER BY date DESC", (q))
        user_habbits = cursor.fetchall()
    # print(user_habbits)

        return render_template('list-connected.html',
                            user_habbits=user_habbits
                            )
    return render_template('list-connected.html')

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    username = request.cookies.get('username')

    q = request.args.get('q')

    cursor.execute("UPDATE habbits SET active = '', mate = '' WHERE q = %s", (q))

    cursor.execute("DELETE FROM habbits WHERE author = %s AND q = %s", (username, q))
    cursor.execute("DELETE FROM active WHERE author = %s AND q = %s", (username, q))
    cursor.execute("UPDATE habbits SET active = %s WHERE q = %s AND author = %s", ('', q, username))
    conn.commit()

    return make_response(redirect(url_for('list_')))

@app.route('/add_active', methods=['POST', 'GET'])
def add_active():
    username = request.cookies.get('username')

    q = request.args.get('q')
    title = request.args.get('title')
    goal = request.args.get('goal')

    cursor.execute("INSERT INTO active (q, title, author, goal) VALUES (%s, %s, %s, %s)", (q, title, username, goal))
    cursor.execute("UPDATE habbits SET active = %s WHERE q = %s AND author = %s", ('+', q, username))
    conn.commit()

    return make_response(redirect(url_for('list_')))

@app.route('/delete_active', methods=['POST', 'GET'])
def delete_active():
    username = request.cookies.get('username')

    q = request.args.get('q')

    cursor.execute("UPDATE habbits SET active = '', mate = '' WHERE q = %s", (q))
    cursor.execute("DELETE FROM active WHERE q = %s AND author = %s", (q, username))
    cursor.execute("UPDATE habbits SET active = %s WHERE q = %s AND author = %s", ('', q, username))
    conn.commit()

    return make_response(redirect(url_for('list_')))

@app.route('/connect', methods=['POST', 'GET'])
def connect():
    username = request.cookies.get('username')
    q = request.args.get('q')

    cursor.execute("UPDATE active SET mate = %s WHERE q = %s", (username, q))
    cursor.execute("UPDATE habbits SET mate = %s WHERE q = %s", (username, q))
    conn.commit()

    return make_response(redirect(url_for('profile') + '#widget'))

@app.route('/new', methods=['POST', 'GET'])
def new():
    return render_template('new.html')

@app.route('/day', methods=['POST', 'GET'])
def day():
    username = request.cookies.get('username')
    q = request.args.get('q')

    cursor.execute("SELECT * FROM active WHERE q = %s AND author = %s", (q, username))
    active_habbit = cursor.fetchall()[0]

    cursor.execute("SELECT max_days FROM users WHERE username = %s", (username))
    max_days = cursor.fetchall()[0][0]
    
    current_date = date.today()
    day = current_date.day

    days = active_habbit[6]

    if int(max_days) < int(days + 1):
        cursor.execute("UPDATE users SET max_days = %s WHERE username = %s", (int(days + 1), username))
        conn.commit()
    
    if str(active_habbit[7]) != str(day):
        cursor.execute("UPDATE active SET last_day = %s, days = %s WHERE q = %s AND author = %s", (day, int(days + 1), q, username))
        conn.commit()

        cursor.execute("SELECT * FROM active WHERE q = %s AND author = %s", (q, username))
        active_habbit_ = cursor.fetchall()[0]

        days = active_habbit_[6]

        goal = active_habbit_[5]
    
        procent = round(((days / goal) * 100), 1)

        cursor.execute("UPDATE active SET procent = %s WHERE q = %s AND author = %s", (procent, q, username))
        conn.commit()
        

    return make_response(redirect(url_for('profile') + '#widget'))

@app.route('/day_mate', methods=['POST', 'GET'])
def day_mate():
    username = request.cookies.get('username')
    q = request.args.get('q')

    cursor.execute("SELECT * FROM active WHERE q = %s AND mate = %s", (q, username))
    active_habbit = cursor.fetchall()[0]

    cursor.execute("SELECT max_days FROM users WHERE username = %s", (username))
    max_days = cursor.fetchall()[0][0]
    
    current_date = date.today()
    day = current_date.day

    days = active_habbit[9]

    if int(max_days) < int(days + 1):
        cursor.execute("UPDATE users SET max_days = %s WHERE username = %s", (int(days + 1), username))
        conn.commit()
    
    if str(active_habbit[10]) != str(day):
        cursor.execute("UPDATE active SET last_day_mate = %s, days_mate = %s WHERE q = %s AND mate = %s", (day, int(days + 1), q, username))
        conn.commit()

        cursor.execute("SELECT * FROM active WHERE q = %s AND mate = %s", (q, username))
        active_habbit_ = cursor.fetchall()[0]

        days = active_habbit_[9]

        goal = active_habbit_[5]
    
        procent = round(((days / goal) * 100), 1)

        cursor.execute("UPDATE active SET procent_mate = %s WHERE q = %s AND mate = %s", (procent, q, username))
        conn.commit()
        

    return make_response(redirect(url_for('profile') + '#widget'))

if __name__ == '__main__':
    # app.run(host='192.168.1.249')
    app.run(host='192.168.173.236')