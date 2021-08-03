from flask import render_template, flash, redirect
import os,binascii
from app import app
from .forms import LoginForm
from flask import request, jsonify
import json
import sqlite3
APP_HOME=os.environ['APP_HOME']
conn = sqlite3.connect(APP_HOME+'/service.db',check_same_thread=False)
from util_c import util
util=util()
#service=util.splunk_conn("config/config.txt")
###########################
def checktoken(vtoken):
###########################
 retflag=0
 c=conn.cursor()
 selsql=""" select token from tokens where token=? """
 c.execute(selsql,  [vtoken]) 
 if len(c.fetchall()) > 0:
    retflag=1
 c.close()
 return retflag
 
###########################
def addtoken(mytoken):
###########################
 c = conn.cursor()
 mytoken=mytoken.decode('utf-8')
 sql="""INSERT INTO tokens (token ) values ('%s') """ % (mytoken)
 print (sql )
 c.execute(sql)
 conn.commit()
 c.close()

#
#--REATE TABLE contacts (first_name varchar(64), last_name varchar(64), email varchar(128), phone varchar(32), zip_code varchar(16) );
###########################
def inscontacts(param):
###########################
 print ("inscontacts", param)
 try:
    c = conn.cursor()
    sql="""INSERT INTO contacts  (first_name, last_name, email, phone, zip_code) values ('%(fname)s','%(lname)s','%(email)s','%(phone)s','%(zip)s' ) """ % param 
    print (sql )
    c.execute(sql)
    conn.commit()
    c.close()
    return 1
 except Exception as e:
    print (str(e) )
    return 0

###########################
def contacts_list():
###########################

 rows=[()]
 try:
    c = conn.cursor()
    sql="""select first_name, last_name, email, phone, zip_code from contacts  """ 
    print (sql )
    c.execute(sql)
    rows=c.fetchall()
    c.close()
    return rows
 except Exception as e:
    print (str(e) )
    return rows

###########################
def update_list():
###########################

 rows=[()]
 try:
    c = conn.cursor()
    sql="""select first_name, last_name, email, phone, zip_code,id from contacts  """   
    print (sql )
    c.execute(sql)
    rows=c.fetchall()
    c.close()
    return rows
 except Exception as e:
    print (str(e) )
    return rows

###########################
def get_contact(p_id):
###########################
 try:
    c = conn.cursor()
    sql="""select first_name, last_name, email, phone, zip_code,id from contacts where id = (%s)  """ % p_id 
    print (sql )
    c.execute(sql)
    rows=c.fetchone()
    c.close()
    return rows
 except Exception as e:
    print (str(e) )
    return rows


###########################
def edit_contact(param):
###########################

 try:
    c = conn.cursor()
    sql="""update contacts set first_name='%(fname)s',
           last_name='%(lname)s' , email='%(email)s', phone='%(phone)s' , zip_code='%(zip)s' 
     where id = %(id)s  
     
""" % param 
    print (sql )
    c.execute(sql)
    c.close()
    return 1   
 except Exception as e:
    print (str(e) )
    return 0   





#
#
#
#
#
# -- Routes ---------------------------
#
#
#
#
# index view function suppressed for brevity
@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Raman', 'firstname':'Raman' , 'lastname':'Kumar'}  # fake user

    posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', 
                           title='Sign In',
                           form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form={}
    if request.method == 'POST':
       email = request.form.get('email')
       mydict=get_user(email)
       if len(mydict) > 0:
          for key in mydict:
              form[key]=mydict[key]
       else:
          form['User']=email+' Not found'
       return render_template('searchoutput.html',title='Search',form=form) 

    else:
       return render_template('search.html', title='Search', form=form)

@app.route('/ip', methods=['GET','POST'])
def ip():
    if request.method == 'GET':
       return jsonify({'ip': 'GET :'+request.remote_addr}), 200
    if request.method == 'POST':
       postdata= json.loads(request.data)
       ip_addrs=request.remote_addr
       print ( postdata['token'] )
       return jsonify({'Got POST': '','data':postdata['token'] }), 200

@app.route('/token',methods=['GET'])
def get_token():
    token=binascii.b2a_hex(os.urandom(15))
    addtoken(token)
    return jsonify({'token': 'Token Created'} ), 200

@app.route('/mypolicy_failures', methods=['GET','POST'])
def mixpanel():
    page=rs.get_rs_data()

    fh=open("app/templates/mixpanel.html","w")
    for line in page:
        fh.write(line)

    fh.close()
    return render_template("mixpanel.html",
                           title='Mixpanel')
#
#

@app.route('/addcontacts', methods=['POST','GET' ])
def addcontacts():
    form={}
    if request.method == 'POST':
       first_name=request.form.get('fname')
       last_name=request.form.get('lname')
       email     =request.form.get('email')
       phone     =request.form.get('phone')
       zip       =request.form.get('zip')
       form={'fname':first_name, 'lname':last_name,'email':email,'phone':phone,'zip':zip }
       if inscontacts(form):
          return render_template('addcontactoutput.html',title=' ',form=form) 
       else:
         return jsonify({'STATUS':'Failed '}  ),299         
    else:
       return render_template('contacts.html',title='Add Contacts',form=form)

@app.route('/listcontacts', methods=['GET' ])
def listcontacts():
    rows=contacts_list()
    return render_template('listcontacts.html',title='List Contacts',rows=rows)

@app.route('/updcontacts', methods=['GET' ])
def updcontacts():
    rows=update_list()
    return render_template('updatecontacts.html',title='Edit Contacts',rows=rows)


@app.route('/editcontacts', methods=['GET', 'POST' ])
def editcontacts():
    id=request.args.get("id")
    if request.method == 'GET':
       rows=get_contact(id)
       return render_template('editcontacts.html',title='Edit Contacts',rows=rows)
    else:
       first_name=request.form.get('fname')
       last_name=request.form.get('lname')
       email     =request.form.get('email')
       phone     =request.form.get('phone')
       zip       =request.form.get('zip')
       id        =request.form.get('id')
       form={'id':id,'fname':first_name, 'lname':last_name,'email':email,'phone':phone,'zip':zip }
       if edit_contact(form):
          return render_template('editcontactsout.html',title='Edit Contacts Completed',form=form)
       else:
          return jsonify({'STATUS': 'Edit failed' }  ),299







