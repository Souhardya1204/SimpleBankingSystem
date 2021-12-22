import pymysql
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, validators,StringField,IntegerField
import time
import datetime
import MySQLdb.cursors
import re

app = Flask(__name__)
sender=""
app.secret_key = 'TIGER'

app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql6460471'
app.config['MYSQL_PASSWORD'] = 'xQJxxs8r63'
app.config['MYSQL_DB'] = 'sql6460471'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# @app.route('/')
# def init():
#     cursor=mysql.connection.cursor()
#     cursor.execute('''create table transactions(
#     sname VARCHAR(100) NOT NULL,
#    rname VARCHAR(100) NOT NULL,
#     amount INT NOT NULL,
#    time DATE NOT NULL DEFAULT CURRENT_TIMESTAMP
# )''')
#     return 'done'
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/customers')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM customers")

    data1 = cursor.fetchall()

    return render_template('customers.html', data=data1)


@app.route('/transaction', methods=['GET', 'POST'])
def make():
    msg = 'Please enter details to be added'
    if request.method == 'POST' and 'cid' in request.form and 'cname' in request.form and 'cemail' in request.form and 'cbal' in request.form:
        user = request.form['cname']
        id = request.form['cid']
        email = request.form['cemail']
        bal = request.form['cbal']
        return render_template('make.html',value1=user,value2=id,value3=email,value4=bal,form={'amount':'','reciever':''})



@app.route("/transactions", methods=['GET', 'POST'])
def transact():
    if request.method == 'POST' and 'reciever' in request.form and 'amount' in request.form and 'pname' in request.form and 'pbal' in request.form:
        global sender
        sender=request.form['pname']
        print(sender)
        checkedForm=Check(request.form)
        if not checkedForm.validate():
                #checkedForm.reciever.errors.append['Sender Receiver cannot be same']
            # if(not request.form['amount'].isnumeric()):
            #     checkedForm.amount.errors.append['Invalid Input']
            #     print('not numeric')
            print(checkedForm.reciever.errors,checkedForm.amount.errors)
            return render_template("make.html",form=checkedForm,value1=request.form['pname'],value2=request.form['id'],value3=request.form['email'],value4=request.form['pbal'])
        else:
            if(sender==request.form['reciever']):
                print('same')
                flash("Sender and Reciever cannot be same","error")
                return render_template("make.html",form=checkedForm,value1=request.form['pname'],value2=request.form['id'],value3=request.form['email'],value4=request.form['pbal'])
            else:
                reciever = request.form['reciever']
                amount=request.form['amount']
                amount1=request.form['amount']
                amount = float(amount)
                amount1 = float(amount1)
                scurrbal = float(request.form['pbal'])
                cursor = mysql.connection.cursor()
                sbal = scurrbal - amount
                cursor.execute("SELECT curr_bal FROM customers WHERE name=%s", (reciever,))
                rcurr_bal = cursor.fetchone()
                rcurrbal = float(rcurr_bal[0])
                rbal = rcurrbal + amount1
                cursor.execute("SELECT * FROM transactions WHERE sname=%s", (sender,))

                tid = cursor.fetchall()
                if scurrbal >= amount:
                    cursor.execute("UPDATE customers SET curr_bal=%s where name=%s", (rbal, reciever,))
                    cursor.execute("UPDATE customers SET curr_bal=%s where name=%s", (sbal, sender,))
                    cursor.execute("INSERT INTO transactions(sname,rname,amount) VALUES ( %s, %s,%s)",
                                (sender, reciever, amount,))
                    mysql.connection.commit()
                else:
                    flash("Insufficient Fund","error")
                    return render_template("make.html",form=checkedForm,value1=request.form['pname'],value2=request.form['id'],value3=request.form['email'],value4=request.form['pbal'])
                return render_template("success.html",transaction='/history',sender=sender,receiver=reciever,sbal=scurrbal,rbal=rbal,amount=amount)
            # return render_template('transact.html',value=tid)


@app.route('/history')
def transhis():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY time DESC')
    data1 = cursor.fetchall()
    return render_template('transaction.html', data=data1)
class Check(Form):
    reciever=StringField('reciever',[validators.DataRequired(),validators.NoneOf([globals()["sender"]],message="sender receiver cannot be same"),validators.Length(min=3,max=25)])
    amount=IntegerField('amount',[validators.DataRequired(),validators.NumberRange(min=1,max=1000000,message="Invalid Input")])


if __name__=='__main__':
    app.run(debug=True)