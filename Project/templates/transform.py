<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learn Spanish — LinguaSphere</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='lang-shared.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* Spanish flag play button */
        .play-btn { background: linear-gradient(to bottom, #AA151B 25%, #F1BF00 25% 75%, #AA151B 75%); }
    </style>
</head>
<body>

    <!-- ═══ NAVBAR ═══ -->
    <header class="navbar">
        <div class="nav-container">
            <a href="/" class="logo-link">
                <div class="logo">
                    <div class="logo-icon-wrap">
                        <svg class="logo-icon" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="22,5 42,15 22,25 2,15" fill="#f5bd05"/>
                            <polygon points="22,7 40,15 22,23 4,15" fill="#ffd04d" opacity="0.3"/>
                            <rect x="10" y="19" width="4" height="11" rx="2" fill="#f5bd05"/>
                            <circle cx="36" cy="15" r="2.5" fill="#fff" opacity="0.9"/>
                            <line x1="36" y1="17.5" x2="36" y2="26" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity="0.85"/>
                            <circle cx="36" cy="27" r="2" fill="#fff" opacity="0.85"/>
                            <circle cx="22" cy="34" r="7" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.9"/>
                            <ellipse cx="22" cy="34" rx="3.5" ry="7" fill="none" stroke="#fff" stroke-width="1.1" opacity="0.65"/>
                            <line x1="15" y1="34" x2="29" y2="34" stroke="#fff" stroke-width="1.1" opacity="0.65"/>
                        </svg>
                    </div>
                    <span class="logo-text"><span class="logo-main">Lingua</span><span class="logo-accent">Sphere</span></span>
                </div>
            </a>
            <nav class="nav-links">
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/about">About Us</a></li>
                    <li class="nav-dropdown">
                        <a href="/languages" class="active dropdown-toggle">Languages <span class="arrow">&#9662;</span></a>
                        <ul class="nav-dropdown-menu">
                            <li><a href="/german">🇩🇪 German</a></li>
                            <li><a href="/spanish">🇪🇸 Spanish</a></li>
                            <li><a href="/italian">🇮🇹 Italian</a></li>
                            <li><a href="/french">🇫🇷 French</a></li>
                        </ul>
                    </li>
                    <li class="nav-dropdown">
                        <a href="/leaderboard" class="dropdown-toggle">Leaderboard <span class="arrow">&#9662;</span></a>
                        <ul class="nav-dropdown-menu">
                            <li><a href="/notebook">📓 Notebook</a></li>
                        </ul>
                    </li>
                </ul>
            </nav>
            <div class="nav-auth">
                {% if 'user_id' in session %}
                <a href="/logout" class="btn-auth btn-logout">Logout</a>
                {% else %}
                <a href="/login" class="btn-auth btn-login">Login</a>
                <a href="/register" class="btn-auth btn-register">Sign Up</a>
                {% endif %}
            </div>
        </div>
    </header>

    <!-- ═══ HERO INTRO ═══ -->
    <section class="lang-intro">
        <div class="lang-intro-container">
            <div class="intro-img-wrap">
                <div class="intro-img-glow"></div>
                <img src="{{ url_for('static', filename='spanish.png') }}" alt="Spanish Learning">
            </div>
            <div class="intro-text">
                <span class="intro-badge">🇪🇸 A1 Level</span>
                <h1 class="intro-title">
                    Learn <span class="intro-highlight">Spanish</span><br>Step by Step
                </h1>
                <p class="intro-desc">
                    Spanish is one of the world's most spoken languages — and one of the most rewarding to learn. Our course focuses on practical phrases, sentence structure, and pronunciation to help you communicate confidently in a variety of real-world situations from day one.
                </p>
                <a href="#lessons" class="intro-cta">Start Listening →</a>
            </div>
        </div>
    </section>

    <!-- ═══ LESSONS ═══ -->
    <div class="lessons-section" id="lessons">
        <div class="lessons-container">

            <!-- Greetings -->
            <div class="lesson-card">
                <div class="lesson-card-header">
                    <span class="lesson-card-icon">👋</span>
                    <h2 class="lesson-card-title">Greetings</h2>
                </div>
                <div class="phrases">
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Hola</span><span class="phrase-meaning">Hello</span></div>
                        <button class="play-btn" onclick="playAudio('hola.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Buen día</span><span class="phrase-meaning">Good day</span></div>
                        <button class="play-btn" onclick="playAudio('buenos-dias.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Buenas noches</span><span class="phrase-meaning">Good evening</span></div>
                        <button class="play-btn" onclick="playAudio('buenas-noches.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Adiós</span><span class="phrase-meaning">Goodbye</span></div>
                        <button class="play-btn" onclick="playAudio('adios.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Nos vemos pronto</span><span class="phrase-meaning">See you soon</span></div>
                        <button class="play-btn" onclick="playAudio('nos-vemo.mp3')" title="Play">▶</button>
                    </div>
                </div>
            </div>

            <!-- Basic Sentences -->
            <div class="lesson-card">
                <div class="lesson-card-header">
                    <span class="lesson-card-icon">💬</span>
                    <h2 class="lesson-card-title">Basic Sentences</h2>
                </div>
                <div class="phrases">
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Mi nombre es…</span><span class="phrase-meaning">My name is…</span></div>
                        <button class="play-btn" onclick="playAudio('Mi nombre es.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Yo Vengo de…</span><span class="phrase-meaning">I come from…</span></div>
                        <button class="play-btn" onclick="playAudio('Yo Vengo de.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Hablo un Poco de español.</span><span class="phrase-meaning">I speak a little Spanish.</span></div>
                        <button class="play-btn" onclick="playAudio('Hablo un Poco de español.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">¿Qué hora es?</span><span class="phrase-meaning">What time is it?</span></div>
                        <button class="play-btn" onclick="playAudio('¿Qué hora es.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">¿Me puedes ayudar?</span><span class="phrase-meaning">Can you help me?</span></div>
                        <button class="play-btn" onclick="playAudio('¿Me puedes ayudar.mp3')" title="Play">▶</button>
                    </div>
                </div>
            </div>

            <!-- Common Phrases -->
            <div class="lesson-card">
                <div class="lesson-card-header">
                    <span class="lesson-card-icon">🗣️</span>
                    <h2 class="lesson-card-title">Common Phrases</h2>
                </div>
                <div class="phrases">
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">¿Cómo estás?</span><span class="phrase-meaning">How are you?</span></div>
                        <button class="play-btn" onclick="playAudio('como-estas.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Gracias</span><span class="phrase-meaning">Thank you</span></div>
                        <button class="play-btn" onclick="playAudio('gracias.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Disculpe</span><span class="phrase-meaning">Excuse me</span></div>
                        <button class="play-btn" onclick="playAudio('disculpe.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">Por favor</span><span class="phrase-meaning">Please</span></div>
                        <button class="play-btn" onclick="playAudio('por-favor.mp3')" title="Play">▶</button>
                    </div>
                    <div class="phrase">
                        <div class="phrase-text"><span class="phrase-foreign">No entiendo</span><span class="phrase-meaning">I don't understand</span></div>
                        <button class="play-btn" onclick="playAudio('noentiendo.mp3')" title="Play">▶</button>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- ═══ QUIZ CTA ═══ -->
    <div class="quiz-strip">
        <div class="quiz-strip-inner">
            <div class="quiz-strip-text">
                <h3>Ready to test your Spanish? 🧠</h3>
                <p>Take the quiz and see how much you've learned from this lesson.</p>
            </div>
            <a href="/spanish_quiz" class="quiz-btn">Take the Quiz →</a>
        </div>
    </div>

    <script>
        function playAudio(filename) {
            const audio = new Audio(`/static/${filename}`);
            audio.play().catch(e => console.error('Audio error:', e));
        }
    </script>
</body>
</html>