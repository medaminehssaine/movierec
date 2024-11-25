from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    with sqlite3.connect('movies.db') as conn:
        c = conn.cursor()
        # Users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        # Movies table
        c.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                username TEXT NOT NULL,
                votes INTEGER DEFAULT 0,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        # Votes table
        c.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                username TEXT,
                movie_id INTEGER,
                PRIMARY KEY (username, movie_id),
                FOREIGN KEY (username) REFERENCES users (username),
                FOREIGN KEY (movie_id) REFERENCES movies (id)
            )
        ''')
        conn.commit()

# Create database tables when app starts
init_db()

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# Register new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400
        
    try:
        with sqlite3.connect('movies.db') as conn:
            c = conn.cursor()
            # Check if username exists
            c.execute('SELECT username FROM users WHERE username = ?', (username,))
            if c.fetchone():
                return jsonify({'message': 'Username already taken'}), 400
                
            # Create new user
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO users VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            return jsonify({'message': 'Registration successful'}), 201
            
    except Exception as e:
        return jsonify({'message': 'Registration failed'}), 500

# Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400
        
    try:
        with sqlite3.connect('movies.db') as conn:
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = c.fetchone()
            
            if not result or not check_password_hash(result[0], password):
                return jsonify({'message': 'Invalid username or password'}), 401
                
            return jsonify({'message': 'Login successful'}), 200
            
    except Exception as e:
        return jsonify({'message': 'Login failed'}), 500

# Get all movies or add a new movie
@app.route('/movies', methods=['GET', 'POST'])
def handle_movies():
    if request.method == 'GET':
        try:
            with sqlite3.connect('movies.db') as conn:
                c = conn.cursor()
                c.execute('''
                    SELECT id, title, description, username, votes 
                    FROM movies 
                    ORDER BY votes DESC
                ''')
                movies = [{
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'username': row[3],
                    'votes': row[4]
                } for row in c.fetchall()]
                return jsonify(movies)
        except Exception as e:
            return jsonify({'message': 'Failed to fetch movies'}), 500

    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        username = data.get('username')
        
        if not all([title, description, username]):
            return jsonify({'message': 'Missing required fields'}), 400
            
        try:
            with sqlite3.connect('movies.db') as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO movies (title, description, username, votes)
                    VALUES (?, ?, ?, 0)
                ''', (title, description, username))
                conn.commit()
                return jsonify({'message': 'Movie added successfully'}), 201
        except Exception as e:
            return jsonify({'message': 'Failed to add movie'}), 500

# Vote for a movie
@app.route('/movies/<int:movie_id>/vote', methods=['POST'])
def vote_movie(movie_id):
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'message': 'Username required'}), 400
        
    try:
        with sqlite3.connect('movies.db') as conn:
            c = conn.cursor()
            # Check if already voted
            c.execute('SELECT * FROM votes WHERE username = ? AND movie_id = ?',
                     (username, movie_id))
            if c.fetchone():
                return jsonify({'message': 'Already voted for this movie'}), 400
                
            # Add vote
            c.execute('INSERT INTO votes VALUES (?, ?)', (username, movie_id))
            c.execute('UPDATE movies SET votes = votes + 1 WHERE id = ?', (movie_id,))
            conn.commit()
            return jsonify({'message': 'Vote recorded'}), 200
            
    except Exception as e:
        return jsonify({'message': 'Voting failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
