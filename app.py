from flask import Flask, render_template, redirect, session, flash
from models import db, connect_db, User, Feedback
from forms import UserRegisterForm, UserLoginForm, FeedbackForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_exercise'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'KEY'

connect_db(app)


@app.route('/')
def home_page():
  if 'curuser' not in session:
    return redirect('/register')
  else:
    return redirect(f'/users/{session["curuser"]}')

@app.route('/register', methods = ['GET', 'POST'])
def register():
  form = UserRegisterForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    new_user = User.register(username, password, email, first_name, last_name)
    db.session.add(new_user)
    db.session.commit()
    session['curuser'] = new_user.username
    flash('Welcome! Successfully Create Your Account!', 'success')
    return redirect(f'/users/{new_user.username}')
  else:
    return render_template('register.html', form = form)
  

@app.route('/login', methods = ['GET', 'POST'])
def login():
  form = UserLoginForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    
    if user:
      flash(f'Welcome Back, {user.username}!', 'primary')
      session['curuser'] = user.username
      return redirect(f'/users/{user.username}')
    else:
      form.username.errors = ['Invalid username/password'] 

  return render_template('login.html', form = form)


@app.route('/users/<username>')
def display_user(username):
  if 'curuser' not in session:
    flash('Please login first!', 'danger')
    return redirect('/login')
  else:
    user = User.query.get_or_404(username)
    feedbacks = user.feedbacks
    return render_template('user.html', user = user, feedbacks = feedbacks)
  

@app.route('/logout', methods = ['POST'])
def logout():
  session.pop('curuser')
  return redirect('/')


@app.route('/users/<username>/feedback/add', methods = ['GET', 'POST'])
def add_feedback(username):
  form = FeedbackForm()

  if form.validate_on_submit():
    title = form.title.data
    content = form.content.data
    feedback = Feedback(title = title, content = content, username = username)
    db.session.add(feedback)
    db.session.commit()
    flash('Feedback created!', 'success')
    return redirect(f'/users/{username}')
  else:
    return render_template('add_feedback.html', form = form)
  

@app.route('/users/<username>/delete', methods = ['POST'])
def delete_user(username):

  if 'curuser' not in session or username != session['curuser']:
    flash("You don't have permission to do it.", 'danger')
    return redirect('/login')

  user = User.query.get_or_404(username)
  db.session.delete(user)
  db.session.commit()
  session.pop('curuser')
  return redirect('/')


@app.route('/feedback/<int:feedback_id>/update', methods = ['GET', 'POST'])
def edit_feedback(feedback_id):
  feedback = Feedback.query.get_or_404(feedback_id)

  if 'curuser' not in session or feedback.username != session['curuser']:
    flash("You don't have permission to do it.", 'danger')
    return redirect('/')
  
  form = FeedbackForm(obj=feedback)

  if form.validate_on_submit():
    feedback.title = form.title.data
    feedback.content = form.content.data

    db.session.commit()

    return redirect(f'/users/{feedback.username}')
  
  return render_template('edit_feedback.html', form = form)


@app.route('/feedback/<int:feedback_id>/delete', methods = ['POST'])
def delete_feedback(feedback_id):
  feedback = Feedback.query.get_or_404(feedback_id)

  if 'curuser' not in session or feedback.username != session['curuser']:
    flash("You don't have permission to do it.", 'danger')
    return redirect('/')
   
  db.session.delete(feedback)
  db.session.commit()

  return redirect(f'/users/{feedback.username}')

