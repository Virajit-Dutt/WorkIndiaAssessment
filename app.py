from dotenv import load_dotenv
import os
import requests
from flask import Flask, request, render_template, session, redirect, url_for, Response
import sqlite3
import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('databases/example.db')
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route('/')
def index():
    # check for session
    if 'username' in session:
        return redirect(url_for('home'))
    
    return render_template('index.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        passwd = request.form['password']
        if name and passwd and email:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            if user:
                return render_template('signup.html', result="User already exists")
            
            if len(passwd) < 6:
                return render_template('signup.html', result="Password too short")
            
            if not any(char.isdigit() for char in passwd):
                return render_template('signup.html', result="Password must have at least one digit")
            
            hashed = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed))
            conn.commit()

            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            print("*** ACCOUNT CREATION DETAILS")
            print(user)
            respo = {"status": "Account successfully created", "status_code": 200, "user_id": user[0]} 
            print(respo)
            return render_template('login.html', result=""), respo

        return render_template('signup.html', result="Failure")
    
    return render_template('signup.html', result="")

@app.route('/login', methods=['POST','GET'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        passwd = request.form['password']
        if email and passwd:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            if user:
                if bcrypt.checkpw(passwd.encode('utf-8'), user[3]):
                    session['username'] = user[1]
                    session['admin'] = False
                    import random
                    session['access_token'] = random.randint(1, 1000000)
                    print("*** LOGIN DETAILS ***")
                    print(user)
                    respo = {"status": "Login successful", "status_code": 200, "user_id": user[0], "access_token": session['access_token']}
                    print(respo)

                    return redirect(url_for('home')), respo
        
        response = {"status": "Incorrect username/password provided. Please retry", "status_code": 401}
        return render_template('login.html', result="Incorrect username/password"), response
    
    return render_template('login.html', result="")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', name=session['username'])
    return redirect(url_for('login'))

@app.route('/admin', methods=['POST','GET'])
def admin():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        passwd = request.form['password']
        if email and passwd:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM admin WHERE email = ?', (email,))
            user = cursor.fetchone()
            if user:
                if (email == user[2]) and (passwd == user[3]):
                    session['username'] = user[1]
                    session['admin'] = True
                    import random
                    session['access_token'] = random.randint(1, 1000000)
                    print("*** LOGIN DETAILS ***")
                    print(user)
                    respo = {"status": "Login successful", "status_code": 200, "user_id": user[0], "access_token": session['access_token']}
                    print(respo)

                    return redirect(url_for('admin_home')), respo
        
        response = {"status": "Incorrect username/password provided. Please retry", "status_code": 401}
        return render_template('admin_login.html', result="Incorrect username/password"), response
    
    return render_template('admin_login.html', result="")

@app.route("/admin_home", methods=['GET'])
def admin_home():
    if 'username' in session:
        return render_template('admin_home.html', name=session['username'])
    return redirect(url_for('admin_login'))

@app.route('/add_restaurant', methods=['POST'])
def add_restaurant():
    if 'username' in session and session['admin']:
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        website = request.form['website']
        opening_hour = request.form['open']
        closing_hour = request.form['close']

        operating_hours = str([opening_hour + " - " + closing_hour])
        print(operating_hours)
        booked_slots = ""
        if name and address and phone and website and operating_hours:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO restaurants (name, address, phone, website, operating_hours, opening_hour, closing_hour, booked_slots) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (name, address, phone, website, operating_hours, opening_hour, closing_hour, booked_slots))
            conn.commit()

            cursor.execute('SELECT * FROM restaurants WHERE name = ?', (name,))
            restaurant = cursor.fetchone()
            print()
            print("*** RESTAURANT CREATION DETAILS ***")
            print(restaurant)
            respo = {"status": restaurant[1]+" added successfully", "status_code": 200, "place_id": restaurant[0]}
            print(respo)
            print()
            return render_template('admin_home.html', result="Restaurant added Successfully"), respo
        return render_template('admin_home.html', result="Restaurant not added")
    return redirect(url_for('admin_login'))

@app.route('/search', methods=['POST'])
def search():
    if 'username' in session:
        search = request.form['name']
        if search:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM restaurants WHERE name LIKE ?', ('%'+search+'%',))
            restaurants = cursor.fetchall()
            print("*** SEARCH RESULTS ***")
            print(restaurants)

            return render_template('restaurant.html', restaurants=restaurants)
        return render_template('home.html', name=session['username'])
    return redirect(url_for('login'))

@app.route('/book/<int:id>', methods=['GET'])
def book(id):
    if 'username' in session:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM restaurants WHERE id = ?', (id,))
        restaurant = cursor.fetchone()
        print("*** RESTAURANT DETAILS ***")
        print(restaurant)

        r2 = {"name": restaurant[1], "address": restaurant[2],"id": restaurant[0]}

        available_slots = []
        if restaurant[8] == "":
            booked=[]
        else:
            booked = restaurant[8].split(',')
            booked = [int(i.split(':')[0]) for i in booked]
        open = int(restaurant[6].split(':')[0])
        close = int(restaurant[7].split(':')[0])

        for i in range(open, close):
            if i not in booked:
                available_slots.append(str(i)+":00 - "+str(i+1)+":00")

        r2['slots'] = available_slots

        print(r2)
        return render_template('book.html', restaurant=r2)
    return redirect(url_for('login'))

@app.route('/confirm_book', methods=['POST'])
def book_post():
    if 'username' in session:
        id = request.form['restaurant_id']
        slot = request.form['slot']
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM restaurants WHERE id = ?', (id,))
        restaurant = cursor.fetchone()
        print("*** RESTAURANT DETAILS ***")
        print(restaurant)

        if restaurant[8] == "":
            booked=[]
        else:
            booked = restaurant[8].split(',')
        booked.append(slot)
        booked = ','.join(booked)
        cursor.execute('UPDATE restaurants SET booked_slots = ? WHERE id = ?', (booked, id))
        conn.commit()

        return redirect(url_for('home'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
