from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
import pyodbc

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# SQL Server connection string
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=YourDatabaseName;'
    'UID=root;'
    'PWD=Poochu@2027;'
)

def get_db_connection():
    return pyodbc.connect(conn_str)

# Database Initialization
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
        CREATE TABLE Users (
            id INT PRIMARY KEY IDENTITY,
            username NVARCHAR(100) UNIQUE NOT NULL,
            password NVARCHAR(200) NOT NULL
        );
    
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Books')
        CREATE TABLE Books (
            id INT PRIMARY KEY IDENTITY,
            title NVARCHAR(200) NOT NULL,
            code NVARCHAR(50) UNIQUE NOT NULL,
            borrowed_by INT NULL,
            borrow_date DATETIME NULL,
            FOREIGN KEY (borrowed_by) REFERENCES Users(id)
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Helper function to create default users
def create_default_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    users = ['23BBS0100', '23BBS0024', 'admin']  # List of usernames
    
    for username in users:
        cursor.execute("SELECT id FROM Users WHERE username = ?", username)
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", username, username)  # Username and password are the same
    
    conn.commit()
    cursor.close()
    conn.close()

# Home route
@app.route('/')
def index():
    return render_template('login.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users WHERE username = ? AND password = ?", username, password)
    user = cursor.fetchone()
    
    if user:
        session['user_id'] = user[0]
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid username or password'})

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, code, borrowed_by, borrow_date FROM Books WHERE borrowed_by = ?", session['user_id'])
    user_books = cursor.fetchall()
    
    cursor.execute("SELECT username FROM Users WHERE id = ?", session['user_id'])
    username = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    # Fetch available books
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, code FROM Books WHERE borrowed_by IS NULL")
    available_books = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('homepage.html', books=user_books, username=username, available_books=available_books)

# Borrow a book
@app.route('/borrow', methods=['POST'])
def borrow_book():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    book_code = request.form['book_code']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books WHERE code = ? AND borrowed_by IS NULL", book_code)
    book = cursor.fetchone()
    
    if book:
        cursor.execute("UPDATE Books SET borrowed_by = ?, borrow_date = ? WHERE code = ?", session['user_id'], datetime.now(), book_code)
        conn.commit()
        cursor.close()
        conn.close()
        flash("Book borrowed successfully!")
        return redirect(url_for('dashboard'))
    
    cursor.close()
    conn.close()
    return "Book not available", 400

# Pay fine (dummy implementation for demonstration)
@app.route('/payfine', methods=['POST'])
def pay_fine():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    # Implement fine payment logic if necessary
    flash("Fine paid successfully!")
    return redirect(url_for('dashboard'))

# Get fine amount
@app.route('/get_fine_amount')
def get_fine_amount():
    # Dummy implementation for fine amount
    fine_amount = 0  # Calculate based on business logic
    return jsonify({'total_fine': fine_amount})

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Initialize the database and add default users
with app.app_context():
    init_db()
    create_default_users()

if __name__ == '__main__':
    app.run(debug=True)
