import sqlite3

conn = sqlite3.connect('databases/example.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE if NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT
    )
''')

cursor.execute('''
    CREATE TABLE if NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT
    )
''')

# create restaurants table
cursor.execute('''
    CREATE TABLE if NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        website TEXT,
        operating_hours TEXT,
        opening_hour TEXT,
        closing_hour TEXT,
        booked_slots TEXT
    )
''')