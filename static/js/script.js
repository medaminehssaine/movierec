        let currentUser = null;

        function showSection(sectionId) {
            document.querySelectorAll('.content').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
        }

        function updateAuthUI() {
            const loggedOutBtns = document.getElementById('loggedOutBtns');
            const loggedInBtns = document.getElementById('loggedInBtns');
            const username = document.getElementById('username');

            if (currentUser) {
                loggedOutBtns.style.display = 'none';
                loggedInBtns.style.display = 'block';
                username.textContent = currentUser;
                showSection('movies');
                loadMovies();
            } else {
                loggedOutBtns.style.display = 'block';
                loggedInBtns.style.display = 'none';
                showSection('login');
            }
        }

        async function login(username, password) {
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });
                const data = await response.json();
                if (response.ok) {
                    currentUser = username;
                    updateAuthUI();
                } else {
                    document.getElementById('loginError').textContent = data.message;
                }
            } catch (error) {
                document.getElementById('loginError').textContent = 'An error occurred';
            }
        }

        async function register(username, password) {
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });
                const data = await response.json();
                if (response.ok) {
                    currentUser = username;
                    updateAuthUI();
                } else {
                    document.getElementById('registerError').textContent = data.message;
                }
            } catch (error) {
                document.getElementById('registerError').textContent = 'An error occurred';
            }
        }

        function logout() {
            currentUser = null;
            updateAuthUI();
        }

        async function loadMovies() {
            try {
                const response = await fetch('/movies');
                const movies = await response.json();
                const movieList = document.getElementById('movieList');
                movieList.innerHTML = '';
                
                movies.forEach(movie => {
                    const movieCard = document.createElement('div');
                    movieCard.className = 'movie-card';
                    movieCard.innerHTML = `
                        <h3 class="movie-title">${movie.title}</h3>
                        <p>${movie.description}</p>
                        <p class="votes">Added by: ${movie.username}</p>
                        <p class="votes">Votes: ${movie.votes}</p>
                        <button onclick="voteMovie(${movie.id})">Vote</button>
                    `;
                    movieList.appendChild(movieCard);
                });
            } catch (error) {
                console.error('Error loading movies:', error);
            }
        }

        async function addMovie(title, description) {
            try {
                const response = await fetch('/movies', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title, description, username: currentUser }),
                });
                if (response.ok) {
                    loadMovies();
                    document.getElementById('movieForm').reset();
                }
            } catch (error) {
                console.error('Error adding movie:', error);
            }
        }

        async function voteMovie(movieId) {
            try {
                const response = await fetch(`/movies/${movieId}/vote`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username: currentUser }),
                });
                if (response.ok) {
                    loadMovies();
                }
            } catch (error) {
                console.error('Error voting:', error);
            }
        }

        // Event Listeners
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            login(username, password);
        });

        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            register(username, password);
        });

        document.getElementById('movieForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const title = document.getElementById('movieTitle').value;
            const description = document.getElementById('movieDescription').value;
            addMovie(title, description);
        });

        // Initialize UI
        updateAuthUI();
