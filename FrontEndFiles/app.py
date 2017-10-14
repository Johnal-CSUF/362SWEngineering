from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init MySQL
mysql = MySQL(app)

#index
@app.route('/')
def index():
	return render_template('home.html')

#about
@app.route('/about')
def about():
	return render_template('about.html')

#reports
@app.route('/reports')
def reports():
	#create cursor
	cur = mysql.connection.cursor()

	#get articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result > 0:
		return render_template('reports.html', articles = articles)
	else:
		msg = 'No Articles Found'
		return render_template('reports.html', msg = msg)

	#close connection
	cur.close()

#single article
@app.route('/report/<string:id>/')
def report(id):
	#create cursor
	cur = mysql.connection.cursor()

	#get article
	result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = cur.fetchone()

	return render_template('report.html', article=article)

#register form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

#user register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

    #user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    	#get form fields
    	username = request.form['username']
    	password_candidate = request.form['password']

    	#create cursor
    	cur = mysql.connection.cursor()

    	#get user by username
    	result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

    	if result > 0:
    		#get stored hash
    		data = cur.fetchone()
    		password = data['password']

    		#compare passwords
    		if sha256_crypt.verify(password_candidate, password):
    			#Passed
    			session['logged_in'] = True
    			session['username'] = username

    			flash('You are now logged in', 'success')
    			return redirect(url_for('dashboard'))
    		else:
    			error = 'Invalid login'
    			return render_template('login.html', error = error)

    		#close connection
    		cur.close()


    	else:
    		error = 'Username not found'
    		return render_template('login.html', error = error)

    return render_template('login.html')

#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap


#logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

#new sales
@app.route('/sales')
@is_logged_in
def sales():
	return render_template('sales.html')

#Discontinued
@app.route('/discontinued')
@is_logged_in
def discontinued():
	return render_template('discontinued.html')

#adding
@app.route('/adding')
@is_logged_in
def adding():
	return render_template('adding.html')

#daily ledge
@app.route('/ledger')
@is_logged_in
def ledger():
	return render_template('daily_ledger.html')

#all reports
@app.route('/all_reports')
@is_logged_in
def all_reports():
		#create cursor
		cur = mysql.connection.cursor()

		#get articles
		result = cur.execute("SELECT * FROM articles")

		articles = cur.fetchall()

		if result > 0:
			return render_template('new_reports.html', articles = articles)
		else:
			msg = 'No Articles Found'
			return render_template('new_reports.html', msg = msg)

		#close connection
		cur.close()

#menu
@app.route('/menu')
@is_logged_in
def menu():
	return render_template('menu.html')

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	#create cursor
	cur = mysql.connection.cursor()

	#get articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result > 0:
		return render_template('dashboard.html', articles = articles)
	else:
		msg = 'No Articles Found'
		return render_template('dashboard.html', msg = msg)

	#close connection
	cur.close()

#articleform class
class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

#add article
@app.route('/add_report', methods=['Get','POST'])
@is_logged_in
def add_report():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		#create cursor
		cur = mysql.connection.cursor()

		#execute
		cur.execute("INSERT INTO articles(title, body, author) VALUE(%s, %s, %s)", (title, body, session['username']))

		#commit to DB
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_report.html', form=form)

#edit article
@app.route('/edit_report/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_report(id):
	#create cursor
	cur = mysql.connection.cursor()

	#get the article by id
	result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

	article = cur.fetchone()

	#get form
	form = ArticleForm(request.form)

	#populate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		#create cursor
		cur = mysql.connection.cursor()

		#execute
		cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))

		#commit to DB
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article Updated', 'success')

		return redirect(url_for('dashboard'))

	return render_template('edit_report.html', form=form)

#delete article
@app.route('/delete_report/<string:id>', methods=['POST'])
@is_logged_in
def delete_report(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)