from flask_login.utils import login_required
from app.forms import ContactForm, DeleteForm, SignUpForm, UserInfoForm, LoginForm 
from flask import render_template, request, redirect, url_for, flash
from flask_wtf.file import FileField, FileRequired
from flask_wtf.form import FlaskForm
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse
from wtforms import validators
from flask_login import current_user, login_user, logout_user, UserMixin, login_required
from app.models import User, Post
from app import app, db, mail
from flask_mail import Message



@app.route('/')
def index():
    context = {
        'title' : 'Home',

    }
    return render_template('index.html', **context)


@app.route('/addcontact', methods=['GET', 'POST'])
@login_required
def addcontact():
    title= 'Add Contact'
    form = ContactForm()
    firstname = form.firstname.data
    lastname = form.lastname.data
    phonenumber = form.phonenumber.data
    workphonenumber = form.workphonenumber.data
    homephonenumber = form.homephonenumber.data
    address = form.address.data
    email = form.email.data
    user_id = current_user.id
    existing_contact = Post.query.filter(Post.phonenumber==phonenumber).all()

    if existing_contact:
        flash('That phone number is already saved in your phone book. Please try again', 'danger')
        return redirect(url_for('contacts'))

    elif request.method == 'POST' and form.validate_on_submit():
        contact = Post(firstname, lastname, email, address, phonenumber, workphonenumber, homephonenumber, user_id)

        db.session.add(contact)
        db.session.commit()
        flash('You have successfully added a contact!', 'success')
        return redirect(url_for('contacts'))

    return render_template('addcontact.html', title=title, form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title='Sign Up'
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # Check if username/email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).all()
        if existing_user:
            flash('That username or email already exists. Please try again', 'danger')
            return redirect(url_for('signup'))
        
        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Thank you {username} for registering!', 'success')

        msg = Message(f'Thank you, {username}', recipients=[email])
        msg.body = f'Dear {username}, thank you for registering for our application and supporting our product. We hope you enjoy this application and look forward to seeing you around. Rest assured, your user information is safe with us. Have an awesome time storing your contacts!'
        mail.send(msg)

        return redirect(url_for('contacts'))


    return render_template('signup.html', title=title, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Login'
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            flash('That is an invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        flash('You have succesfully logged in!', 'success')
        return redirect(url_for('contacts'))

    return render_template('login.html', title=title, form=form)



@app.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    context = {
        'title' : 'Contacts',
        'posts' : Post.query.filter_by(user_id=current_user.id).all()
}
    return render_template('contacts.html', **context)



@app.route('/logout')
def logout():
    logout_user()
    flash('You have logged out! Hate to see you go, but love watching you leave.' , 'info')
    return redirect(url_for('index'))

@app.route('/contactsupdate/<int:post_id>', methods=['GET', 'POST'])
@login_required
def contact_update(post_id):
    contact = Post.query.get_or_404(post_id)
    title = 'Update Contact'
    update_form = ContactForm()
    if request.method == 'POST' and update_form.validate_on_submit():
        fn = update_form.firstname.data
        ln = update_form.lastname.data
        pn = update_form.phonenumber.data
        wpn = update_form.workphonenumber.data
        hpn = update_form.homephonenumber.data
        add = update_form.address.data
        email = update_form.email.data

        contact.firstname = fn
        contact.lastname = ln
        contact.phonenumber = pn
        contact.workphonenumber = wpn
        contact.homephonenumber = hpn
        contact.address = add
        contact.email = email

        db.session.commit()
        return redirect(url_for('contacts', post_id=contact.id))
    return render_template('contactsupdate.html', form=update_form, post=contact, title=title)



@app.route('/delete/<int:post_id>')
@login_required
def delete(post_id):
    contact_to_delete= Post.query.get_or_404(post_id)
    try:
        db.session.delete(contact_to_delete)
        db.session.commit()
        flash('Contact has been deleted', 'primary')
        return redirect(url_for('contacts'))
    except:
        flash("There was a problem deleting that contact", 'danger')
        return redirect(url_for('contacts'))

    