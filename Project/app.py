from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
import bcrypt
from functools import wraps
import random
from wtforms import RadioField, SubmitField

app = Flask(__name__)  # Fixed typo here
app.secret_key = 'your_secret_key_here'

# Enable CSRF Protection
csrf = CSRFProtect(app)

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")
    
    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        users = cursor.fetchone()
        cursor.close()
        if users:
            raise ValidationError('Email Already Taken')
        
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

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_database'

mysql = MySQL(app)

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
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Store data into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        users = cursor.fetchone()
        cursor.close()
        
        if users and bcrypt.checkpw(password.encode('utf-8'), users[3].encode('utf-8')):
            session['user_id'] = users[0]
            session['username'] = users[1]
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Login failed. Please check your email and password.")
    
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
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        message = form.message.data

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO contact (first_name, last_name, email, message) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, email, message)
        )
        mysql.connection.commit()
        cursor.close()

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html', form=form)

@app.route('/languages')
def languages():
    return render_template('languages.html')

@app.route('/german')
@login_required
def german():
    return render_template('german.html')

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


@app.route('/german_quiz', methods=['GET', 'POST'])
@login_required
def german_quiz():
    form = GermanQuizForm()

    # Check if a question index is stored in the session
    if 'current_question' not in session:
        question_index = random.randint(0, len(questions) - 1)
        session['current_question'] = question_index
    else:
        question_index = session['current_question']

    question = questions[question_index]
    form.answer.choices = [(option, option) for option in question['options']]

    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data

        # Check if the user's answer is correct
        if user_answer == question['correct']:
            result = "Correct!"
        else:
            result = f"Incorrect! The correct answer was: {question['correct']}"

        # Clear the session to generate a new question
        session.pop('current_question', None)

    return render_template('german_quiz.html', form=form, question=question,result=result)

@app.route('/spanish')
@login_required
def spanish():
    return render_template('spanish.html') 

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

@app.route('/spanish_quiz', methods=['GET', 'POST'])
@login_required
def spanish_quiz():
    form = SpanishQuizForm()

    # Check if a question index is stored in the session
    if 'current_question' not in session:
        question_index = random.randint(0, len(questions1) - 1)
        session['current_question'] = question_index
    else:
        question_index = session['current_question']

    question1 = questions1[question_index]
    form.answer.choices = [(option, option) for option in question1['options']]

    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data

        # Check if the user's answer is correct
        if user_answer == question1['correct']:
            result = "Correct!"
        else:
            result = f"Incorrect! The correct answer was: {question1['correct']}"

        # Clear the session to generate a new question
        session.pop('current_question', None)

    return render_template('spanish_quiz.html', form=form, question1=question1,result=result)

@app.route('/italian')
@login_required
def italian():
    return render_template('italian.html') 

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

@app.route('/italian_quiz', methods=['GET', 'POST'])
@login_required
def italian_quiz():
    form = ItalianQuizForm()

    # Check if a question index is stored in the session
    if 'current_question' not in session:
        question_index = random.randint(0, len(questions2) - 1)
        session['current_question'] = question_index
    else:
        question_index = session['current_question']

    question2 = questions2[question_index]
    form.answer.choices = [(option, option) for option in question2['options']]

    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data

        # Check if the user's answer is correct
        if user_answer == question2['correct']:
            result = "Correct!"
        else:
            result = f"Incorrect! The correct answer was: {question2['correct']}"

        # Clear the session to generate a new question
        session.pop('current_question', None)

    return render_template('italian_quiz.html', form=form, question2=question2,result=result)


@app.route('/french')
@login_required
def french():
    return render_template('french.html') 

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

@app.route('/french_quiz', methods=['GET', 'POST'])
@login_required
def french_quiz():
    form = FrenchQuizForm()

    # Check if a question index is stored in the session
    if 'current_question' not in session:
        question_index = random.randint(0, len(questions3) - 1)
        session['current_question'] = question_index
    else:
        question_index = session['current_question']

    question3 = questions3[question_index]
    form.answer.choices = [(option, option) for option in question3['options']]

    result = None
    if form.validate_on_submit():
        user_answer = form.answer.data

        # Check if the user's answer is correct
        if user_answer == question3['correct']:
            result = "Correct!"
        else:
            result = f"Incorrect! The correct answer was: {question3['correct']}"

        # Clear the session to generate a new question
        session.pop('current_question', None)

    return render_template('french_quiz.html', form=form, question3=question3,result=result)

if __name__ == '__main__': 
    app.run(debug=True)