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

#single report
@app.route('/report/<string:id>/')
def report(id):
	#create cursor
	cur = mysql.connection.cursor()

	#get report
	result = cur.execute("SELECT * FROM basicReports WHERE id = %s", [id])

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

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        mysql.connection.commit()

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

#daily ledger
@app.route('/ledger')
@is_logged_in
def ledger():
	return render_template('daily_ledger.html')

#adding
@app.route('/adding')
@is_logged_in
def adding():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM customers")
	customers = cur.fetchall()

	resultTwo = cur.execute("SELECT * FROM orders")
	orders = cur.fetchall()

	if result > 0 and resultTwo > 0:
		return render_template('adding.html', customers = customers, orders = orders)
	if result > 0 and resultTwo == 0:
		msg = 'No Customers Found'
		return render_template('adding.html', customers = customers, msg = msg)
	if result == 0 and resultTwo > 0:
		msg = 'No Customers Found'
		return render_template('adding.html', msg = msg, orders = orders)
	else:
		msg = 'No Customers or Orders Found'
		return render_template('adding.html', msg = msg)

	cur.close()

#all reports
@app.route('/all_reports')
@is_logged_in
def all_reports():
		cur = mysql.connection.cursor()

		result = cur.execute("SELECT * FROM basicReports")
		basicReports = cur.fetchall()

		if result > 0:
			return render_template('all_reports.html', basicReports = basicReports)
		else:
			msg = 'No Reports Found'
			return render_template('all_reports.html', msg = msg)

		cur.close()

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM basicReports")
	basicReports = cur.fetchall()

	if result > 0:
		return render_template('dashboard.html', basicReports = basicReports)
	else:
		msg = 'No Reports Found'
		return render_template('dashboard.html', msg = msg)

	#close connection
	cur.close()

#BasicReportForm class
class BasicReportForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

#add basic report
@app.route('/add_basicReport', methods=['Get','POST'])
@is_logged_in
def add_basicReport():
	form = BasicReportForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO basicReports(title, body, author) VALUE(%s, %s, %s)", (title, body, session['username']))

		mysql.connection.commit()
		cur.close()

		flash('Report Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_basicReport.html', form=form)

#edit basic report
@app.route('/edit_basicReport/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_basicReport(id):
	cur = mysql.connection.cursor()

	#get the article by id
	result = cur.execute("SELECT * FROM basicReports WHERE id = %s", [id])
	article = cur.fetchone()

	form = BasicReportForm(request.form)

	#populate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		cur = mysql.connection.cursor() #create cursor
		cur.execute("UPDATE basicReports SET title=%s, body=%s WHERE id=%s", (title, body, id)) #execute
		mysql.connection.commit() #commit to DB

		cur.close() #close connection

		flash('Report Updated', 'success')
		return redirect(url_for('dashboard'))

	return render_template('edit_basicReport.html', form=form)

#delete basic article
@app.route('/delete_basicReport/<string:id>', methods=['POST'])
@is_logged_in
def delete_basicReport(id):
    cur = mysql.connection.cursor() # Create cursor
    cur.execute("DELETE FROM basicReports WHERE id = %s", [id]) # Execute

    mysql.connection.commit() # Commit to DB
    cur.close() #Close connection

    flash('Report Deleted', 'success')
    return redirect(url_for('all_reports'))

#CustomerForm class
class CustomerForm(Form):
	CustID = StringField('Customer ID', [validators.Length(min=5, max=10)])
	Fname = StringField('First Name', [validators.Length(min=1, max=20)])
	Lname = StringField('Last Name', [validators.Length(min=1, max=30)])
	phone = StringField('Phone', [validators.Length(min=10, max=15)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	#YTD_Sales = StringField('Phone', [validators.Length(min=5, max=20)])

#add customer
@app.route('/add_customer', methods=['Get','POST'])
@is_logged_in
def add_customer():
	form = CustomerForm(request.form)
	if request.method == 'POST' and form.validate():
		CustID = form.CustID.data
		Fname = form.Fname.data
	 	Lname= form.Lname.data
		phone = form.phone.data
		email = form.email.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO customers(CustID, Fname, Lname, phone, email) VALUES(%s, %s, %s, %s, %s)", (CustID, Fname, Lname, phone, email))

		mysql.connection.commit()
		cur.close()

		flash('Customer Added', 'success')
		return redirect(url_for('adding'))

	return render_template('add_customer.html', form=form)

#edit customer
@app.route('/edit_customer/<string:CustID>', methods=['GET', 'POST'])
@is_logged_in
def edit_customer(CustID):
	cur = mysql.connection.cursor()

	#get the article by id
	result = cur.execute("SELECT * FROM customers WHERE CustID = %s", [id])
	customer = cur.fetchone()

	form = CustomerForm(request.form)

	#populate article form fields
	form.CustID.data = customer['CustID']
	form.Fname.data = customer['Fname']
	form.Lname.data = customer['Lname']
	form.phone.data = customer['Phone']
	form.email.data = customer['Email']

	if request.method == 'POST' and form.validate():
		CustID = form.CustID.data
		Fname = form.Fname.data
	 	Lname= form.Lname.data
		phone = form.phone.data
		email = form.email.data

		cur = mysql.connection.cursor() #create cursor

		cur.execute("UPDATE customers SET CustID=%s, Fname=%s, Lname=%s, phone=%s, email=%s WHERE CustID=%s", (CustID, Fname, Lname, phone, email, id))
		mysql.connection.commit() #commit to DB

		cur.close() #close connection

		flash('Customer Updated', 'success')
		return redirect(url_for('adding'))

	return render_template('edit_customer.html', form=form)

#delete customer
@app.route('/delete_customer/<string:id>', methods=['POST'])
@is_logged_in
def delete_customer(id):
    cur = mysql.connection.cursor() # Create cursor

    cur.execute("DELETE FROM customers WHERE id = %s", [id]) # Execute
    mysql.connection.commit() # Commit to DB

    cur.close() #Close connection

    flash('Customer Deleted', 'success')
    return redirect(url_for('adding'))

#OrderForm class
class OrderForm(Form):
	ItemNumber = StringField('Item Number', [validators.Length(min=1, max=5)])
	CustID = StringField('Customer ID', [validators.Length(min=1, max=5)])
	OrderDate = StringField('Order Date (mm/dd/yyyy)', [validators.Length(min=6, max=15)])
	Quantity = StringField('Quantity', [validators.Length(min=1, max=5)])

#add order
@app.route('/add_order', methods=['Get','POST'])
@is_logged_in
def add_order():
	form = OrderForm(request.form)
	if request.method == 'POST' and form.validate():
		ItemNumber = form.ItemNumber.data
		CustID = form.CustID.data
	 	OrderDate = form.OrderDate.data
		Quantity = form.Quantity.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO orders(ItemNumber, CustID, OrderDate, Quantity) VALUES(%s, %s, %s, %s)", (ItemNumber, CustID, OrderDate, Quantity))

		mysql.connection.commit()
		cur.close()

		flash('Order Added', 'success')
		return redirect(url_for('adding'))

	return render_template('add_order.html', form=form)

#edit customer
@app.route('/edit_order/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_order(id):
	cur = mysql.connection.cursor()

	#get the article by id
	result = cur.execute("SELECT * FROM orders WHERE id = %s", [id])
	orders = cur.fetchone()

	#get form
	form = CustomerForm(request.form)

	#populate article form fields
	form.ItemNumber.data = customer['ItemNumber']
	form.CustID.data = customer['CustID']
	form.OrderDate.data = customer['OrderDate']
	form.Quantity.data = customer['Quantity']

	if request.method == 'POST' and form.validate():
		ItemNumber = form.ItemNumber.data
		CustID = form.CustID.data
	 	OrderDate = form.OrderDate.data
		Quantity = form.Quantity.data

		cur = mysql.connection.cursor() #create cursor

		cur.execute("UPDATE orders SET ItemNumber=%s, CustID=%s, OrderDate=%s, Quantity=%s WHERE id=%s", (ItemNumber,CustID, OrderDate, Quantity, id))
		mysql.connection.commit() #commit to DB

		cur.close() #close connection

		flash('Order Updated', 'success')
		return redirect(url_for('adding'))

	return render_template('edit_order.html', form=form)

#delete customer
@app.route('/delete_order/<string:id>', methods=['POST'])
@is_logged_in
def delete_order(id):
    cur = mysql.connection.cursor() # Create cursor

    cur.execute("DELETE FROM orders WHERE id = %s", [id]) # Execute
    mysql.connection.commit() # Commit to DB

    cur.close() #Close connection

    flash('Order Deleted', 'success')
    return redirect(url_for('adding'))

#InventoryReportForm class
class InventoryReportForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

#add Inventory Report
@app.route('/add_inventoryReport', methods=['Get','POST'])
@is_logged_in
def add_inventoryReport():
	form = InventoryReportForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO inventoryReports(title, body, author) VALUE(%s, %s, %s)", (title, body, session['username']))

		mysql.connection.commit()
		cur.close()

		flash('Report Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_inventoryReport.html', form=form)

#edit inventory report
@app.route('/edit_inventoryReport/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_inventoryReport(id):
	cur = mysql.connection.cursor()

	#get the article by id
	result = cur.execute("SELECT * FROM inventoryReports WHERE id = %s", [id])
	article = cur.fetchone()

	form = InventoryReportForm(request.form)

	#populate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		cur = mysql.connection.cursor() #create cursor

		cur.execute("UPDATE inventoryReports SET title=%s, body=%s WHERE id=%s", (title, body, id)) #execute
		mysql.connection.commit() #commit to DB

		cur.close() #close connection

		flash('Report Updated', 'success')
		return redirect(url_for('dashboard'))

	return render_template('edit_inventoryReport.html', form=form)

#delete inventory article
@app.route('/delete_inventoryReport/<string:id>', methods=['POST'])
@is_logged_in
def delete_inventoryReport(id):
    cur = mysql.connection.cursor() # Create cursor

    cur.execute("DELETE FROM inventoryReports WHERE id = %s", [id]) # Execute
    mysql.connection.commit() # Commit to DB

    cur.close() #Close connection

    flash('Report Deleted', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)
