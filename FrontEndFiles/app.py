from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__, static_url_path='/static')

#config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

#Newsletter Form class
class NewsletterForm(Form):
	email = StringField('Email', [validators.Length(min=1, max=200)])

#index
@app.route('/', methods=['Get','POST'])
def index():
	form = NewsletterForm(request.form)
	if request.method == 'POST' and form.validate():
		email = form.email.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO newsletter(email) VALUE(%s)", (email,))

		mysql.connection.commit()
		cur.close()

		flash('Congrats! You Are Now In Our Newsletter!', 'success')
		return redirect(url_for('about'))

	return render_template('home.html', form=form)

#about
@app.route('/about')
def about():
	return render_template('about.html')

#register form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords do not match')])
	confirm = PasswordField('Confirm Password')
	manager = StringField('Manager? ("yes" or "no")', [validators.Length(min=2, max=3)])

#user register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		manager = form.manager.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(name, email, username, password, manager) VALUES(%s, %s, %s, %s, %s)", (name, email, username, password, manager))

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
    			session['logged_in'] = True
    			session['username'] = username

    			flash('You are now logged in', 'success')
    			return redirect(url_for('dashboard'))
    		else:
    			error = 'Invalid login'
    			return render_template('login.html', error = error)

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

#user list
@app.route('/user_list')
@is_logged_in
def user_list():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM users")
	users = cur.fetchall()

	if result > 0:
		return render_template('user_list.html', users=users)
	else:
		msg = 'No Users Found'
		return render_template('user_list.html', msg = msg)

	cur.close()

#delete user
@app.route('/delete_user/<string:id>', methods=['POST'])
@is_logged_in
def delete_user(id):
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM users WHERE id = %s", [id])
    mysql.connection.commit()

    cur.close()

    flash('User Deleted', 'success')
    return redirect(url_for('user_list'))

#logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

#adding
@app.route('/adding')
@is_logged_in
def adding():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM customers")
	customers = cur.fetchall()

	resultTwo = cur.execute("SELECT * FROM orders")
	orders = cur.fetchall()

	resultThree = cur.execute("SELECT * FROM products")
	products = cur.fetchall()

	if result > 0 and resultTwo > 0 and resultThree > 0:
		return render_template('adding.html', customers=customers, orders=orders, products=products)
	if result > 0 and resultTwo == 0 and resultThree > 0:
		msg = 'No Sales Found'
		return render_template('adding.html', customers = customers, products=products, msg=msg)
	if result == 0 and resultTwo > 0 and resultThree > 0:
		msg = 'No Customers Found'
		return render_template('adding.html', msg = msg, products=products, orders = orders)
	else:
		msg = 'No Customers or Sales or Products Found'
		return render_template('adding.html', msg = msg)

	cur.close()

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM users")
	users = cur.fetchall()

	return render_template('dashboard.html', users=users)
	cur.close()

#Customer Form class
class CustomerForm(Form):
	CustID = StringField('Customer ID', [validators.Length(min=1, max=5)])
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

#delete customer
@app.route('/delete_customer/<string:CustID>', methods=['POST'])
@is_logged_in
def delete_customer(CustID):
    cur = mysql.connection.cursor() # Create cursor

    cur.execute("DELETE FROM customers WHERE CustID = %s", [CustID]) # Execute
    mysql.connection.commit() # Commit to DB

    cur.close() #Close connection

    flash('Customer Deleted', 'success')
    return redirect(url_for('adding'))

#Order Form class
class OrderForm(Form):
	ItemNumber = StringField('Item Number', [validators.Length(min=1, max=5)])
	CustID = StringField('Customer ID', [validators.Length(min=1, max=5)])
	OrderDate = StringField('Order Date (mm/dd/yyyy)', [validators.Length(min=6, max=15)])
	Quantity = StringField('Quantity', [validators.Length(min=1, max=5)])

#add sale
@app.route('/add_sale', methods=['Get','POST'])
@is_logged_in
def add_sale():
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

		flash('Sale Added', 'success')
		return redirect(url_for('sale'))

	return render_template('add_sale.html', form=form)

#sale
@app.route('/sale', methods=['Get','POST'])
@is_logged_in
def sale():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM orders")
	orders = cur.fetchall()

	if result > 0:
		return render_template('sale.html', orders=orders)
	else:
		msg = 'No Sales Found'
		return render_template('sale.html', msg = msg)

	cur.close()

#delete sale
@app.route('/delete_sale/<string:ItemNumber>', methods=['POST'])
@is_logged_in
def delete_sale(ItemNumber):
    cur = mysql.connection.cursor() # Create cursor

    cur.execute("DELETE FROM orders WHERE ItemNumber = %s", [ItemNumber])
    mysql.connection.commit() # Commit to DB

    cur.close() #Close connection

    flash('Sale Deleted', 'success')
    return redirect(url_for('sale'))


#Product Form class
class ProductForm(Form):
	ItemNumber = StringField('Item Number', [validators.Length(min=1, max=5)])
	Description = StringField('Description', [validators.Length(min=5, max=20)])
	Price = StringField('Price', [validators.Length(min=3, max=10)])
	inventory_amount = StringField('Inventory Amount', [validators.Length(min=1, max=5)])
	Class = StringField('Class', [validators.Length(min=2, max=10)])
	Origin = StringField('Origin', [validators.Length(min=2, max=15)])
	Lead_Time = StringField('Lead Time', [validators.Length(min=5, max=20)])

#add products
@app.route('/add_product', methods=['Get','POST'])
@is_logged_in
def add_product():
	form = ProductForm(request.form)
	if request.method == 'POST' and form.validate():
		ItemNumber = form.ItemNumber.data
		Description = form.Description.data
	 	Price = form.Price.data
		inventory_amount = form.inventory_amount.data
		Class = form.Class.data
		Origin = form.Origin.data
		Lead_Time = form.Lead_Time.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO products(ItemNumber, Description, Price, inventory_amount, Class, Origin, Lead_Time) VALUES(%s, %s, %s, %s, %s, %s, %s)", (ItemNumber, Description, Price, inventory_amount, Class, Origin, Lead_Time))

		mysql.connection.commit()
		cur.close()

		flash('Product Added', 'success')
		return redirect(url_for('adding'))

	return render_template('add_product.html', form=form)

#delete product
@app.route('/delete_product/<string:ItemNumber>', methods=['POST'])
@is_logged_in
def delete_product(ItemNumber):
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM products WHERE ItemNumber = %s", [ItemNumber])
    mysql.connection.commit()

    cur.close()

    flash('Product Deleted', 'success')
    return redirect(url_for('adding'))

#Reorder
@app.route('/reorder')
@is_logged_in
def reroder():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM products WHERE inventory_amount = 0")
	products = cur.fetchall()

	if result > 0:
		return render_template('reorder.html', products=products)
	else:
		msg = 'No Items Need to be Reordered'
		return render_template('reorder.html', msg=msg)

	cur.close();

#End of Day + Logout
@app.route('/end_day_report')
@is_logged_in
def end_day_report():
	session.clear()
	flash('You are now logged out', 'success')

	cur = mysql.connection.cursor()

	resultTwo = cur.execute("SELECT * FROM orders")
	orders = cur.fetchall()

	result = cur.execute("SELECT * FROM customers")
	customers = cur.fetchall()

	resultThree = cur.execute("SELECT * FROM products")
	products = cur.fetchall()

	if result > 0 and resultTwo > 0 and resultThree > 0:
		return render_template('end_day_report.html', orders=orders, customers=customers, products=products)
	if result > 0 and resultTwo == 0 and resultThree > 0:
		msg = 'No Sales Found'
		return render_template('end_day_report.html', customers = customers, products=products, msg=msg)
	if result == 0 and resultTwo > 0 and resultThree > 0:
		msg = 'No Customers Found'
		return render_template('end_day_report.html', msg = msg, products=products, orders = orders)
	else:
		msg = 'No Customers or Sales or Products Found'
		return render_template('end_day_report.html', msg = msg)

	#close connection
	cur.close()

#Report Form class
class ReportForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/report')
@is_logged_in
def report():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM reports")
	reports = cur.fetchall()

	if result > 0:
		return render_template('report.html', reports=reports)
	else:
		msg = 'No Reports Found'
		return render_template('report.html', msg = msg)

	cur.close()

#single report
@app.route('/individual_report/<string:id>/')
def individual_report(id):
	#create cursor
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM reports WHERE id = %s", [id])

	report = cur.fetchone()
	return render_template('individual_report.html', report=report)

#add report
@app.route('/add_report', methods=['Get','POST'])
@is_logged_in
def add_report():
	form = ReportForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO reports(title, body, author) VALUE(%s, %s, %s)", (title, body, session['username']))

		mysql.connection.commit()
		cur.close()

		flash('Report Created', 'success')
		return redirect(url_for('report'))

	return render_template('add_report.html', form=form)

#edit report
@app.route('/edit_report/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_report(id):

	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM reports WHERE id = %s", [id])

	report = cur.fetchone()
	form = ReportForm(request.form)

	form.title.data = report['title']
	form.body.data = report['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		cur = mysql.connection.cursor()
		cur.execute("UPDATE reports SET title=%s, body=%s WHERE id=%s", (title, body, id))

		mysql.connection.commit()
		cur.close()

		flash('Report Updated', 'success')
		return redirect(url_for('report'))

	return render_template('edit_report.html', form=form)


#delete report
@app.route('/delete_report/<string:id>', methods=['POST'])
@is_logged_in
def delete_report(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM reports WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Report Deleted', 'success')

    return redirect(url_for('report'))


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)
