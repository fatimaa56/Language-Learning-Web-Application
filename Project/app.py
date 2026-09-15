from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_wtf.csrf import CSRFProtect
import bcrypt
from functools import wraps
import random
from wtforms import RadioField, SubmitField
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Enable CSRF Protection
csrf = CSRFProtect(app)

# ─────────────────────────────────────────────
# MongoDB Configuration
# ─────────────────────────────────────────────
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['language_learning_db']
quiz_scores_collection = mongo_db['quiz_scores']
saved_words_collection = mongo_db['saved_words']
users_collection = mongo_db['users']
contacts_collection = mongo_db['contacts']
notes_collection = mongo_db['notes']           # NEW: Notepad
friendships_collection = mongo_db['friendships']  # NEW: Friends leaderboard

# ─────────────────────────────────────────────
# Forms
# ─────────────────────────────────────────────
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name")
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit")

class GermanQuizForm(FlaskForm):
    answer = RadioField('Answer', choices=[], coerce=str, validators=[DataRequired()])
    submit = SubmitField('Submit Answer')

class SpanishQuizForm(FlaskForm):
    answer = RadioField('Answer', choices=[], coerce=str, validators=[DataRequired()])
    submit = SubmitField('Submit Answer')

class ItalianQuizForm(FlaskForm):
    answer = RadioField('Answer', choices=[], coerce=str, validators=[DataRequired()])
    submit = SubmitField('Submit Answer')

class FrenchQuizForm(FlaskForm):
    answer = RadioField('Answer', choices=[], coerce=str, validators=[DataRequired()])
    submit = SubmitField('Submit Answer')


# ─────────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────────
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ─────────────────────────────────────────────
# Basic Routes
# ─────────────────────────────────────────────
@app.route('/')
@nocache
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
@nocache
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already registered!")
            return redirect(url_for('register'))
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now()
        })
        flash("Registration successful!")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = users_collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password!")
    return render_template('login.html', form=form)

@app.route('/logout')
@nocache
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
@nocache
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contacts_collection.insert_one({
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "message": form.message.data,
            "created_at": datetime.now()
        })
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/languages')
def languages():
    return render_template('languages.html')


# ─────────────────────────────────────────────
# Quiz Questions Data
# ─────────────────────────────────────────────
questions = [
    {"question": "Hallo", "options": ["Goodbye", "Good day", "Hello", "See you soon"], "correct": "Hello"},
    {"question": "Guten Tag", "options": ["Hello", "Good evening", "See you soon", "Good day"], "correct": "Good day"},
    {"question": "Guten Abend", "options": ["Good day", "Good evening", "Hello", "Goodbye"], "correct": "Good evening"},
    {"question": "Auf Wiedersehen", "options": ["Please", "Goodbye", "Excuse me", "Thank you"], "correct": "Goodbye"},
    {"question": "Bis bald", "options": ["Good evening", "See you soon", "Good day", "How are you?"], "correct": "See you soon"},
    {"question": "Ich heiße...", "options": ["My name is...", "I come from...", "I don't understand", "What time is it?"], "correct": "My name is..."},
    {"question": "Ich komme aus...", "options": ["I don't understand", "Can you help me?", "I come from...", "I speak a little German"], "correct": "I come from..."},
    {"question": "Ich spreche ein bisschen Deutsch.", "options": ["I speak a little German", "Can you help me?", "I come from...", "My name is..."], "correct": "I speak a little German"},
    {"question": "Wie spät ist es?", "options": ["How are you?", "What time is it?", "I don't understand", "Please"], "correct": "What time is it?"},
    {"question": "Können Sie mir helfen?", "options": ["Can you help me?", "I speak a little German", "Thank you", "Excuse me"], "correct": "Can you help me?"}
]

questions1 = [
    {"question1": "Hola", "options": ["Goodbye", "Good day", "Hello", "See you soon"], "correct": "Hello"},
    {"question1": "Buenos días", "options": ["Hello", "Good evening", "See you soon", "Good day"], "correct": "Good day"},
    {"question1": "Buenas noches", "options": ["Good day", "Good evening", "Hello", "Goodbye"], "correct": "Good evening"},
    {"question1": "Adiós", "options": ["Please", "Goodbye", "Excuse me", "Thank you"], "correct": "Goodbye"},
    {"question1": "Hasta pronto", "options": ["Good evening", "See you soon", "Good day", "How are you?"], "correct": "See you soon"},
    {"question1": "Me llamo...", "options": ["My name is...", "I come from...", "I don't understand", "What time is it?"], "correct": "My name is..."},
    {"question1": "Soy de...", "options": ["I don't understand", "Can you help me?", "I come from...", "I speak a little Spanish"], "correct": "I come from..."},
    {"question1": "Hablo un poco de español.", "options": ["I speak a little Spanish", "Can you help me?", "I come from...", "My name is..."], "correct": "I speak a little Spanish"},
    {"question1": "¿Qué hora es?", "options": ["How are you?", "What time is it?", "I don't understand", "Please"], "correct": "What time is it?"},
    {"question1": "¿Puede ayudarme?", "options": ["Can you help me?", "I speak a little Spanish", "Thank you", "Excuse me"], "correct": "Can you help me?"}
]

questions2 = [
    {"question2": "Ciao", "options": ["Goodbye", "Good day", "Hello", "See you soon"], "correct": "Hello"},
    {"question2": "Buongiorno", "options": ["Hello", "Good evening", "See you soon", "Good day"], "correct": "Good day"},
    {"question2": "Buonasera", "options": ["Good day", "Good evening", "Hello", "Goodbye"], "correct": "Good evening"},
    {"question2": "Arrivederci", "options": ["Please", "Goodbye", "Excuse me", "Thank you"], "correct": "Goodbye"},
    {"question2": "A presto", "options": ["Good evening", "See you soon", "Good day", "How are you?"], "correct": "See you soon"},
    {"question2": "Mi chiamo...", "options": ["My name is...", "I come from...", "I don't understand", "What time is it?"], "correct": "My name is..."},
    {"question2": "Vengo da...", "options": ["I don't understand", "Can you help me?", "I come from...", "I speak a little Italian"], "correct": "I come from..."},
    {"question2": "Parlo un po' di italiano.", "options": ["I speak a little Italian", "Can you help me?", "I come from...", "My name is..."], "correct": "I speak a little Italian"},
    {"question2": "Che ore sono?", "options": ["How are you?", "What time is it?", "I don't understand", "Please"], "correct": "What time is it?"},
    {"question2": "Può aiutarmi?", "options": ["Can you help me?", "I speak a little Italian", "Thank you", "Excuse me"], "correct": "Can you help me?"}
]

questions3 = [
    {"question3": "Bonjour", "options": ["Goodbye", "Good day", "Hello", "See you soon"], "correct": "Hello"},
    {"question3": "Bonsoir", "options": ["Hello", "Good evening", "See you soon", "Good day"], "correct": "Good evening"},
    {"question3": "Salut", "options": ["Good day", "Goodbye", "Hello", "Excuse me"], "correct": "Hello"},
    {"question3": "Au revoir", "options": ["Please", "Goodbye", "Excuse me", "Thank you"], "correct": "Goodbye"},
    {"question3": "À bientôt", "options": ["Good evening", "See you soon", "Good day", "How are you?"], "correct": "See you soon"},
    {"question3": "Je m'appelle...", "options": ["My name is...", "I come from...", "I don't understand", "What time is it?"], "correct": "My name is..."},
    {"question3": "Je viens de...", "options": ["I don't understand", "Can you help me?", "I come from...", "I speak a little French"], "correct": "I come from..."},
    {"question3": "Je parle un peu français.", "options": ["I speak a little French", "Can you help me?", "I come from...", "My name is..."], "correct": "I speak a little French"},
    {"question3": "Quelle heure est-il?", "options": ["How are you?", "What time is it?", "I don't understand", "Please"], "correct": "What time is it?"},
    {"question3": "Pouvez-vous m'aider?", "options": ["Can you help me?", "I speak a little French", "Thank you", "Excuse me"], "correct": "Can you help me?"}
]


# ─────────────────────────────────────────────
# Language Pages
# ─────────────────────────────────────────────
@app.route('/german')
@login_required
def german():
    return render_template('german.html')

@app.route('/spanish')
@login_required
def spanish():
    return render_template('spanish.html')

@app.route('/italian')
@login_required
def italian():
    return render_template('italian.html')

@app.route('/french')
@login_required
def french():
    return render_template('french.html')


# ─────────────────────────────────────────────
# Quiz Routes
# ─────────────────────────────────────────────
@app.route('/german_quiz', methods=['GET', 'POST'])
@login_required
def german_quiz():
    form = GermanQuizForm()
    if 'current_question' not in session:
        session['current_question'] = random.randint(0, len(questions) - 1)
    question_index = session['current_question']
    question = questions[question_index]
    form.answer.choices = [(option, option) for option in question['options']]
    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data
        is_correct = user_answer == question['correct']
        result = "Correct! 🎉" if is_correct else f"Incorrect! The correct answer was: {question['correct']}"
        quiz_scores_collection.insert_one({
            "user_id": str(session['user_id']),
            "username": session['username'],
            "language": "German",
            "question": question['question'],
            "user_answer": user_answer,
            "correct_answer": question['correct'],
            "is_correct": is_correct,
            "score": 1 if is_correct else 0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now()
        })
        session.pop('current_question', None)
    return render_template('german_quiz.html', form=form, question=question, result=result)


@app.route('/spanish_quiz', methods=['GET', 'POST'])
@login_required
def spanish_quiz():
    form = SpanishQuizForm()
    if 'current_question' not in session:
        session['current_question'] = random.randint(0, len(questions1) - 1)
    question_index = session['current_question']
    question1 = questions1[question_index]
    form.answer.choices = [(option, option) for option in question1['options']]
    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data
        is_correct = user_answer == question1['correct']
        result = "Correct! 🎉" if is_correct else f"Incorrect! The correct answer was: {question1['correct']}"
        quiz_scores_collection.insert_one({
            "user_id": str(session['user_id']),
            "username": session['username'],
            "language": "Spanish",
            "question": question1['question1'],
            "user_answer": user_answer,
            "correct_answer": question1['correct'],
            "is_correct": is_correct,
            "score": 1 if is_correct else 0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now()
        })
        session.pop('current_question', None)
    return render_template('spanish_quiz.html', form=form, question1=question1, result=result)


@app.route('/italian_quiz', methods=['GET', 'POST'])
@login_required
def italian_quiz():
    form = ItalianQuizForm()
    if 'current_question' not in session:
        session['current_question'] = random.randint(0, len(questions2) - 1)
    question_index = session['current_question']
    question2 = questions2[question_index]
    form.answer.choices = [(option, option) for option in question2['options']]
    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data
        is_correct = user_answer == question2['correct']
        result = "Correct! 🎉" if is_correct else f"Incorrect! The correct answer was: {question2['correct']}"
        quiz_scores_collection.insert_one({
            "user_id": str(session['user_id']),
            "username": session['username'],
            "language": "Italian",
            "question": question2['question2'],
            "user_answer": user_answer,
            "correct_answer": question2['correct'],
            "is_correct": is_correct,
            "score": 1 if is_correct else 0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now()
        })
        session.pop('current_question', None)
    return render_template('italian_quiz.html', form=form, question2=question2, result=result)


@app.route('/french_quiz', methods=['GET', 'POST'])
@login_required
def french_quiz():
    form = FrenchQuizForm()
    if 'current_question' not in session:
        session['current_question'] = random.randint(0, len(questions3) - 1)
    question_index = session['current_question']
    question3 = questions3[question_index]
    form.answer.choices = [(option, option) for option in question3['options']]
    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data
        is_correct = user_answer == question3['correct']
        result = "Correct! 🎉" if is_correct else f"Incorrect! The correct answer was: {question3['correct']}"
        quiz_scores_collection.insert_one({
            "user_id": str(session['user_id']),
            "username": session['username'],
            "language": "French",
            "question": question3['question3'],
            "user_answer": user_answer,
            "correct_answer": question3['correct'],
            "is_correct": is_correct,
            "score": 1 if is_correct else 0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now()
        })
        session.pop('current_question', None)
    return render_template('french_quiz.html', form=form, question3=question3, result=result)


# ─────────────────────────────────────────────
# FEATURE 1: Enhanced Leaderboard (MongoDB)
# ─────────────────────────────────────────────
@app.route('/leaderboard')
@login_required
def leaderboard():
    tab = request.args.get('tab', 'global')
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def build_pipeline(match_stage=None):
        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})
        pipeline += [
            {"$group": {
                "_id": "$username",
                "total_correct": {"$sum": "$score"},
                "total_attempts": {"$sum": 1}
            }},
            {"$addFields": {
                "accuracy": {
    "$cond": {
        "if": {"$gt": ["$total_attempts", 0]},
        "then": {"$multiply": [{"$divide": ["$total_correct", "$total_attempts"]}, 100]},
        "else": 0
    }
}

            }},
            {"$sort": {"total_correct": -1}},
            {"$limit": 10}
        ]
        return pipeline

    global_board = list(quiz_scores_collection.aggregate(build_pipeline()))
    weekly_board = list(quiz_scores_collection.aggregate(build_pipeline({"timestamp": {"$gte": week_start}})))
    monthly_board = list(quiz_scores_collection.aggregate(build_pipeline({"timestamp": {"$gte": month_start}})))

    # Friends leaderboard
    friend_usernames = list(friendships_collection.find(
        {"user_id": str(session['user_id'])}, {"_id": 0, "friend_username": 1}
    ))
    friend_names = [f['friend_username'] for f in friend_usernames] + [session['username']]
    friends_board = list(quiz_scores_collection.aggregate(
        build_pipeline({"username": {"$in": friend_names}})
    ))

    # My stats per language
    user_pipeline = [
        {"$match": {"user_id": str(session['user_id'])}},
        {"$group": {
            "_id": "$language",
            "correct": {"$sum": "$score"},
            "attempts": {"$sum": 1}
        }},
        {"$sort": {"correct": -1}}
    ]
    my_stats = list(quiz_scores_collection.aggregate(user_pipeline))

    # My global rank
    all_users = list(quiz_scores_collection.aggregate(build_pipeline()))
    my_rank = next((i + 1 for i, u in enumerate(all_users) if u['_id'] == session['username']), None)

    # Badge logic
    my_total = next((u['total_correct'] for u in all_users if u['_id'] == session['username']), 0)
    badge = None
    if my_total >= 50:
        badge = "🏅 Master Linguist"
    elif my_total >= 20:
        badge = "⭐ Rising Star"
    elif my_total >= 10:
        badge = "🌱 Dedicated Learner"
    elif my_total >= 1:
        badge = "✨ Quiz Rookie"

    # All users for friend search
    all_usernames = [u['username'] for u in users_collection.find({}, {"username": 1})]

    return render_template('leaderboard.html',
        global_board=global_board,
        weekly_board=weekly_board,
        monthly_board=monthly_board,
        friends_board=friends_board,
        my_stats=my_stats,
        my_rank=my_rank,
        badge=badge,
        tab=tab,
        friend_names=friend_names,
        all_usernames=all_usernames
    )


@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    data = request.get_json()
    friend_username = data.get('username', '').strip()
    if not friend_username:
        return jsonify({"success": False, "message": "No username provided."})
    if friend_username == session['username']:
        return jsonify({"success": False, "message": "You can't add yourself!"})
    user_exists = users_collection.find_one({"username": friend_username})
    if not user_exists:
        return jsonify({"success": False, "message": "User not found."})
    existing = friendships_collection.find_one({
        "user_id": str(session['user_id']),
        "friend_username": friend_username
    })
    if existing:
        return jsonify({"success": False, "message": "Already in your friends list!"})
    friendships_collection.insert_one({
        "user_id": str(session['user_id']),
        "username": session['username'],
        "friend_username": friend_username,
        "added_at": datetime.now()
    })
    return jsonify({"success": True, "message": f"{friend_username} added to friends!"})


@app.route('/remove_friend', methods=['POST'])
@login_required
def remove_friend():
    data = request.get_json()
    friend_username = data.get('username', '').strip()
    friendships_collection.delete_one({
        "user_id": str(session['user_id']),
        "friend_username": friend_username
    })
    return jsonify({"success": True, "message": f"{friend_username} removed."})


# ─────────────────────────────────────────────
# FEATURE 2: Vocabulary Notebook (MongoDB)
# ─────────────────────────────────────────────
@app.route('/save_word', methods=['POST'])
@csrf.exempt
@login_required
def save_word():
    data = request.get_json()
    word = (data.get('word') or '').strip()
    meaning = (data.get('meaning') or '').strip()
    language = (data.get('language') or '').strip()
    if not word or not meaning or not language:
        return jsonify({"success": False, "message": "Missing data"}), 400
    existing = saved_words_collection.find_one({
        "user_id": str(session['user_id']),
        "word": word
    })
    if existing:
        return jsonify({"success": False, "message": "Word already in notebook!"})
    saved_words_collection.insert_one({
        "user_id": str(session['user_id']),
        "username": session['username'],
        "language": language,
        "word": word,
        "meaning": meaning,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return jsonify({"success": True, "message": "Word saved to your notebook!"})


@app.route('/notebook')
@login_required
def notebook():
    words = list(saved_words_collection.find(
        {"user_id": str(session['user_id'])},
        {"_id": 0}
    ).sort("saved_at", -1))
    return render_template('notebook.html', words=words)


@app.route('/delete_word', methods=['POST'])
@csrf.exempt
@login_required
def delete_word():
    data = request.get_json()
    word = data.get('word')
    saved_words_collection.delete_one({
        "user_id": str(session['user_id']),
        "word": word
    })
    return jsonify({"success": True})


# ─────────────────────────────────────────────
# FEATURE 3: Full Notepad (MongoDB)
# ─────────────────────────────────────────────
@app.route('/notepad')
@login_required
@nocache
def notepad():
    search_q = request.args.get('search', '').strip()
    tag_filter = request.args.get('tag', '').strip()
    sort_by = request.args.get('sort', 'updated_at')
    category_filter = request.args.get('category', '').strip()

    query = {"user_id": str(session['user_id'])}
    if search_q:
        query["$or"] = [
            {"title": {"$regex": search_q, "$options": "i"}},
            {"content": {"$regex": search_q, "$options": "i"}},
            {"tags": {"$regex": search_q, "$options": "i"}}
        ]
    if tag_filter:
        query["tags"] = tag_filter
    if category_filter:
        query["category"] = category_filter

    sort_field = sort_by if sort_by in ['updated_at', 'created_at', 'title'] else 'updated_at'
    sort_dir = 1 if sort_field == 'title' else -1

    notes = list(notes_collection.find(query).sort(sort_field, sort_dir))
    for note in notes:
        note['_id'] = str(note['_id'])

    # Get all tags used by user
    all_tags_raw = notes_collection.distinct("tags", {"user_id": str(session['user_id'])})
    all_tags = [t for t in all_tags_raw if t]

    # Categories
    all_categories = notes_collection.distinct("category", {"user_id": str(session['user_id'])})
    all_categories = [c for c in all_categories if c]

    return render_template('notepad.html',
        notes=notes,
        search_q=search_q,
        tag_filter=tag_filter,
        sort_by=sort_by,
        all_tags=all_tags,
        all_categories=all_categories,
        category_filter=category_filter
    )


@app.route('/notepad/create', methods=['POST'])
@csrf.exempt
@login_required
def create_note():
    data = request.get_json()
    title = data.get('title', 'Untitled').strip() or 'Untitled'
    content = data.get('content', '')
    tags = [t.strip() for t in data.get('tags', '').split(',') if t.strip()]
    category = data.get('category', 'General').strip() or 'General'
    pinned = data.get('pinned', False)
    favorite = data.get('favorite', False)

    note_id = notes_collection.insert_one({
        "user_id": str(session['user_id']),
        "username": session['username'],
        "title": title,
        "content": content,
        "tags": tags,
        "category": category,
        "pinned": pinned,
        "favorite": favorite,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }).inserted_id

    return jsonify({"success": True, "note_id": str(note_id), "message": "Note created!"})


@app.route('/notepad/update/<note_id>', methods=['POST'])
@csrf.exempt
@login_required
def update_note(note_id):
    data = request.get_json()
    update_fields = {"updated_at": datetime.now()}
    if 'title' in data:
        update_fields['title'] = data['title'].strip() or 'Untitled'
    if 'content' in data:
        update_fields['content'] = data['content']
    if 'tags' in data:
        update_fields['tags'] = [t.strip() for t in data['tags'].split(',') if t.strip()]
    if 'category' in data:
        update_fields['category'] = data['category'].strip() or 'General'
    if 'pinned' in data:
        update_fields['pinned'] = bool(data['pinned'])
    if 'favorite' in data:
        update_fields['favorite'] = bool(data['favorite'])

    notes_collection.update_one(
        {"_id": ObjectId(note_id), "user_id": str(session['user_id'])},
        {"$set": update_fields}
    )
    return jsonify({"success": True, "message": "Note saved!"})


@app.route('/notepad/delete/<note_id>', methods=['POST'])
@csrf.exempt
@login_required
def delete_note(note_id):
    notes_collection.delete_one({
        "_id": ObjectId(note_id),
        "user_id": str(session['user_id'])
    })
    return jsonify({"success": True, "message": "Note deleted."})


@app.route('/notepad/get/<note_id>')
@login_required
def get_note(note_id):
    note = notes_collection.find_one({
        "_id": ObjectId(note_id),
        "user_id": str(session['user_id'])
    })
    if not note:
        return jsonify({"success": False}), 404
    note['_id'] = str(note['_id'])
    note['created_at'] = note['created_at'].strftime("%Y-%m-%d %H:%M") if note.get('created_at') else ''
    note['updated_at'] = note['updated_at'].strftime("%Y-%m-%d %H:%M") if note.get('updated_at') else ''
    return jsonify({"success": True, "note": note})


@app.route('/notepad/export/<note_id>')
@login_required
def export_note(note_id):
    fmt = request.args.get('format', 'txt')
    note = notes_collection.find_one({
        "_id": ObjectId(note_id),
        "user_id": str(session['user_id'])
    })
    if not note:
        flash("Note not found.", "danger")
        return redirect(url_for('notepad'))

    if fmt == 'txt':
        content = f"Title: {note['title']}\n"
        content += f"Category: {note.get('category', 'General')}\n"
        content += f"Tags: {', '.join(note.get('tags', []))}\n"
        content += f"Created: {note.get('created_at', '').strftime('%Y-%m-%d %H:%M') if note.get('created_at') else ''}\n"
        content += f"\n{note.get('content', '')}"
        response = make_response(content)
        response.headers['Content-Disposition'] = f'attachment; filename="{note["title"]}.txt"'
        response.headers['Content-Type'] = 'text/plain'
        return response

    # PDF export (simple HTML-based)
    html_content = f"""
    <html><head><style>
    body {{ font-family: Georgia, serif; padding: 40px; color: #2d2d2d; }}
    h1 {{ color: #7c3aed; }} .meta {{ color: #888; font-size: 0.9em; margin-bottom: 20px; }}
    .content {{ line-height: 1.8; white-space: pre-wrap; }}
    </style></head><body>
    <h1>{note['title']}</h1>
    <div class='meta'>Category: {note.get('category','General')} | Tags: {', '.join(note.get('tags',[]))} | {note.get('created_at','').strftime('%Y-%m-%d') if note.get('created_at') else ''}</div>
    <div class='content'>{note.get('content','')}</div>
    </body></html>
    """
    response = make_response(html_content)
    response.headers['Content-Disposition'] = f'attachment; filename="{note["title"]}.html"'
    response.headers['Content-Type'] = 'text/html'
    return response


if __name__ == '__main__':
    app.run(debug=True)