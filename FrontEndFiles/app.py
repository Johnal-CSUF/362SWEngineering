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

#register form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords do not match')])
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
		return render_template('adding.html', msg = msg)

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
	return render_template('dashboard.html')

#CustomerForm class
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

#edit customer
@app.route('/edit_customer/<string:CustID>', methods=['GET', 'POST'])
@is_logged_in
def edit_customer(CustID):
	cur = mysql.connection.cursor()

	#get the article by id
	result = cur.execute("SELECT * FROM customers WHERE CustID = %s", [CustID])
	customer = cur.fetchone()

	form = CustomerForm(request.form)

	#populate article form fields
	form.CustID.data = customer['CustID']
	form.Fname.data = customer['Fname']
	form.Lname.data = customer['Lname']
	form.phone.data = customer['Phone']
	form.email.data = customer['Email']

	if request.method == 'POST' and form.validate():
		CustID = request.form['CustID']
		Fname = request.form['Fname']
	 	Lname= request.form['Lname']
		phone = request.form['Phone']
		email = request.form['Email']

		cur = mysql.connection.cursor() #create cursor
		cur.execute("UPDATE customers SET CustID=%s, Fname=%s, Lname=%s, phone=%s, email=%s WHERE CustID=%s", (CustID, Fname, Lname, phone, email, CustID))
		mysql.connection.commit() #commit to DB

		cur.close()
		flash('Customer Updated', 'success')
		return redirect(url_for('adding'))

	return render_template('edit_customer.html', form=form)

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

#OrderForm class
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
		return redirect(url_for('adding'))

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

#edit sale
@app.route('/edit_sale/<string:ItemNumber>', methods=['GET', 'POST'])
@is_logged_in
def edit_sale(ItemNumber):
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM orders WHERE ItemNumber = %s", [ItemNumber])
	order = cur.fetchone()

	form = OrderForm(request.form)

	form.ItemNumber.data = order['ItemNumber']
	form.CustID.data = order['CustID']
	form.OrderDate.data = order['OrderDate']
	form.Quantity.data = order['Quantity']

	if request.method == 'POST' and form.validate():
		ItemNumber = request.form['Item Number']
		CustID = request.form['Customer ID']
	 	OrderDate = request.form['Order Date (mm/dd/yyyy)']
		Quantity = request.form['Quantity']

		cur = mysql.connection.cursor() #create cursor

		cur.execute("UPDATE orders SET ItemNumber=%s, CustID=%s, OrderDate=%s, Quantity=%s WHERE ItemNumber=%s", (ItemNumber,CustID, OrderDate, Quantity, ItemNumber))
		mysql.connection.commit() #commit to DB

		cur.close() #close connection

		flash('Order Updated', 'success')
		return redirect(url_for('adding'))

	return render_template('edit_sale.html', form=form)

#delete sale
@app.route('/delete_sale/<string:ItemNumber>', methods=['POST'])
@is_logged_in
def delete_sale(ItemNumber):
    cur = mysql.connection.cursor() # Create cursor

    cur.execute("DELETE FROM orders WHERE ItemNumber = %s", [ItemNumber])
    mysql.connection.commit() # Commit to DB

    cur.close() #Close connection

    flash('Sale Deleted', 'success')
    return redirect(url_for('adding'))


#ProductForm class
class ProductForm(Form):
	ItemNumber = StringField('Item Number', [validators.Length(min=1, max=5)])
	Description = StringField('Description', [validators.Length(min=5, max=20)])
	Price = StringField('Price', [validators.Length(min=3, max=10)])
	Available = StringField('Available', [validators.Length(min=1, max=5)])
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
		Available = form.Available.data
		Class = form.Class.data
		Origin = form.Origin.data
		Lead_Time = form.Lead_Time.data

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO products(ItemNumber, Description, Price, Available, Class, Origin, Lead_Time) VALUES(%s, %s, %s, %s, %s, %s, %s)", (ItemNumber, Description, Price, Available, Class, Origin, Lead_Time))

		mysql.connection.commit()
		cur.close()

		flash('Product Added', 'success')
		return redirect(url_for('adding'))

	return render_template('add_product.html', form=form)

#edit product
@app.route('/edit_product/<string:ItemNumber>', methods=['GET', 'POST'])
@is_logged_in
def edit_product(ItemNumber):
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM products WHERE ItemNumber = %s", [ItemNumber])
	product = cur.fetchone()

	form = ProductForm(request.form)

	form.ItemNumber.data = product['ItemNumber']
	form.Description.data = product['Description']
	form.Price.data = product['Price']
	form.Available.data = product['Available']
	form.Class.data = product['Class']
	form.Origin.data = product['Origin']
	form.Lead_Time.data = product['Lead_Time']

	if request.method == 'POST' and form.validate():
		ItemNumber = request.form['Item Number']
		Description= request.form['Description']
	 	Price = request.form['Price']
		Available = request.form['Available']
		Class = request.form['Class']
		Origin = request.form['Origin']
		Lead_Time = request.form['Lead Time']

		cur = mysql.connection.cursor() #create cursor

		cur.execute("UPDATE products SET ItemNumber=%s, Description=%s, Price=%s, Available=%s, Class=%s, Origin=%s, Lead_Time=%s WHERE ItemNumber=%s", (ItemNumber, Description, Price, Available, Class, Origin, Lead_Time, ItemNumber))
		mysql.connection.commit()

		cur.close()

		flash('Product Updated', 'success')
		return redirect(url_for('adding'))

	return render_template('edit_product.html', form=form)

#delete customer
@app.route('/delete_product/<string:ItemNumber>', methods=['POST'])
@is_logged_in
def delete_product(ItemNumber):
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM product WHERE ItemNumber = %s", [ItemNumber])
    mysql.connection.commit()

    cur.close()

    flash('Product Deleted', 'success')
    return redirect(url_for('adding'))

#Reorder
@app.route('/reorder')
@is_logged_in
def reroder():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM products WHERE Available = 0")
	products = cur.fetchall()

	if result > 0:
		return render_template('reorder.html', products=products)
	else:
		msg = 'No Items Need to be Reordered'
		return render_template('reorder.html', msg=msg)

	cur.close();

#edit product
@app.route('/order_form/<string:ItemNumber>', methods=['GET', 'POST'])
@is_logged_in
def order_form(ItemNumber):
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM products WHERE ItemNumber = %s", [ItemNumber])
	product = cur.fetchone()

	form = ProductForm(request.form)

	form.ItemNumber.data = product['ItemNumber']
	form.Description.data = product['Description']
	form.Price.data = product['Price']
	form.Class.data = product['Class']
	form.Origin.data = product['Origin']
	form.Available.data = product['Available']

	if request.method == 'POST' and form.validate():
		ItemNumber = request.form['Item Number']
		Description= request.form['Description']
	 	Price = request.form['Price']
		Class = request.form['Class']
		Origin = request.form['Origin']
		Available = request.form['Amount To Restock']

		cur = mysql.connection.cursor() #create cursor

		cur.execute("UPDATE products SET ItemNumber=%s, Description=%s, Price=%s, Class=%s, Origin=%s, Available=%s WHERE ItemNumber=%s", (ItemNumber, Description, Price, Class, Origin, Available, ItemNumber))
		mysql.connection.commit()

		cur.close()

		flash('Product Ordered', 'success')
		return redirect(url_for('adding'))

	return render_template('order_form.html', form=form)

#End of Day + Logout
@app.route('/end_day_report')
@is_logged_in
def end_day_report():
	session.clear()
	flash('You are now logged out', 'success')

	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM customers")
	customers = cur.fetchall()

	resultTwo = cur.execute("SELECT * FROM products")
	products = cur.fetchall()

	if result > 0 and resultTwo > 0:
		return render_template('adding.html', customers=customers, products=products)
	if result > 0 and resultTwo == 0:
		msg = 'No Products Found'
		return render_template('adding.html', msg = msg, customers=customers, products=products)
	if result == 0 and resultTwo > 0:
		msg = 'No Customers Found'
		return render_template('adding.html', msg = msg, customers=customers, products=products)
	else:
		msg = 'No Customers or Products Found'
		return render_template('dashboard.html', msg = msg)

	cur.close()
	return redirect(url_for('end_day_report'))


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)
