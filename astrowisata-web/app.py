import sys
import os
from functools import wraps
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_session import Session
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, SelectField, DateField, IntegerRangeField
from wtforms.validators import DataRequired,EqualTo, Length, InputRequired, Regexp
#from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_migrate import Migrate
#from hashlib import sha256
from werkzeug.utils import secure_filename
import mysql.connector
#from mysql.connector.constants import ClientFlag
from datetime import datetime, date, timedelta
import bcrypt
from flaskext.mysql import MySQL
from PIL import Image
from io import BytesIO
import uuid as uuid
import numpy as np


app = Flask(__name__)
#mysql = MySQL()
app.secret_key= " "
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
VERIFICATION_FOLDER = 'static/verification'
app.config['VERIFICATION_FOLDER'] = VERIFICATION_FOLDER
PAYMENT_FOLDER = 'static/payment'
app.config['PAYMENT_FOLDER'] = PAYMENT_FOLDER
IMAGES_FOLDER = 'static/images'
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER
PROOF_FOLDER = 'static/proofs'
app.config['PROOF_FOLDER'] = PROOF_FOLDER


#mysql.init_app(app)
#conn = mysql.connect()
#cur = mysql.connection.cursor()


#try:
mydb =  mysql.connector.connect(
    host="db host",
    user="db username",
    password="db password",
    database="db")


    #message = 'Successfully Connected'
mycursor = mydb.cursor()

#except mysql.connector.Error as e:
 #   message = "Not Connected"

#FORMS
class UserForm(FlaskForm):
    name = StringField("Nama Usaha/ Destinasi", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Regexp(r'^[\w.@+-]+$')])
    nomor = IntegerField ("Nomor Whatsapp", validators=[DataRequired()])
    deskripsi = TextAreaField ("Deskripsi Usaha/Destinasi", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must match")])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField ("Daftar")
    
class ConsumerForm(FlaskForm):
    title = SelectField(u"Titel",choices=[('Tuan', 'Tuan'),('Nyonya', 'Nyonya'), 
                                                         ('Nona','Nona' )])
    name = StringField("Nama", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])  
    username = StringField("Username", validators=[DataRequired(), Regexp(r'^[\w.@+-]+$')])
    nomor = IntegerField ("Nomor HP", validators=[DataRequired()])
    nationality = SelectField(u"Kebangsaan",choices=[('Indonesia', 'Indonesia'),('Malaysia', 'Malaysia'), 
                                                         ('Singapura','Singapura' ), ('Cina', 'Cina'),
                                                         ('Australia', 'Australia'), ('India', 'India'),
                                                         ('Timor Leste', 'Timor Leste'), ('Korea Selatan', 'Korea Selatan'),
                                                         ('Amerika', 'Amerika'), ('Jepang', 'Jepang'), ('Inggris', 'Inggris')])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must match")])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField ("Daftar") 

class ContributorsForm(FlaskForm):
    name = StringField("Nama", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])  
    username = StringField("Username", validators=[DataRequired(), Regexp(r'^[\w.@+-]+$')])
    nomor = IntegerField ("Nomor Whatsapp", validators=[DataRequired()])
    verification = FileField('Kartu Tanda Mahasiswa/ Identifikasi Dosen', validators=[FileRequired(), FileAllowed(['jpg','png', 'jpeg', 'HEIC'])])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must match")])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField ("Daftar")      
    
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField ("Masuk")
class PostForm(FlaskForm):
    title = StringField("Judul", validators=[DataRequired()])
    content = TextAreaField ("Deskripsi", validators=[DataRequired()])
    event_date = DateField("Tanggal mulai",validators=[DataRequired()])
    event_end = DateField("Tanggal selesai",validators=[DataRequired()])
    location = StringField("Lokasi", validators=[DataRequired()])
    type_of_event = SelectField(u"Tipe kegiatan",choices=[('Stargazing', 'Stargazing'),('Gerhana Matahari', 'Gerhana Matahari'), 
                                                         ('Gerhana Bulan','Gerhana Bulan' ), ('Komet', 'Komet'),
                                                         ('Hujan Meteor', 'Hujan Meteor'), ('Starbath', 'Starbath'),
                                                         ('Pengamatan Planet', 'Pengamatan Planet'), ('Planetarium', 'Planetarium'),
                                                         ('Tempat Bersejarah', 'Tempat Bersejarah')])
    price = StringField('Harga paket', validators=[DataRequired()])
    image_1 = FileField('Gambar', validators=[FileAllowed(['jpg','png', 'jpeg', 'HEIC', 'gif'])])
    submit = SubmitField ("Tambahkan Paket") 
    
class CartForm(FlaskForm):
    quantity = IntegerField('Jumlah', validators=[DataRequired()])
    start_date = DateField("Tanggal Keberangkatan",validators=[DataRequired()])
    end_date = DateField("Tanggal Kepulangan",validators=[DataRequired()])
    submit = SubmitField ("Tambahkan ke Keranjang")   
    editcart = SubmitField("Simpan")    

class CheckoutForm(FlaskForm):
    payment = FileField('Bukti pembayaran', validators=[FileRequired(), FileAllowed(['jpg','png', 'jpeg', 'HEIC', 'gif'])])
    identity_num = IntegerField ("Nomor Identitas", validators=[DataRequired()])
    dob = DateField("Tanggal lahir",validators=[DataRequired()])
    submit = SubmitField ("Kirim") 

class RateForm(FlaskForm):
    rate = IntegerRangeField('Nilai', validators=[DataRequired()])
    review = TextAreaField('Komentar', validators=[DataRequired()])
    submit = SubmitField ("Kirim Penilaian")    

class ArticleForm(FlaskForm):
    title = StringField("Judul", validators=[DataRequired()])
    content = TextAreaField ("Isi", validators=[DataRequired()])
    image_1 = FileField('Gambar', validators=[FileAllowed(['jpg','png', 'jpeg', 'HEIC', 'gif'])])
    verification = FileField('Bukti telah diperiksa dosen', validators=[FileAllowed(['jpg','png', 'jpeg', 'HEIC', 'gif', 'pdf'])])
    link = StringField("Tautan sumber atau tautan terkait artikel")
    article_type = SelectField(u"Kategori Artikel",choices=[('Tata Surya', 'Tata Surya'),('Gerhana', 'Gerhana'), 
                                                         ('Kosmologi','Kosmologi' ), ('Galaksi', 'Galaksi'),
                                                         ('Bintang', 'Bintang'), ('Astrowisata', 'Astrowisata'),
                                                         ('Menjawab Hoax', 'Menjawab Hoax'),('Alam Semesta','Alam Semesta'), 
                                                         ('Lainnya', 'Lainnya')])
    submit = SubmitField ("Tambahkan artikel")

class EventForm(FlaskForm):
    title = StringField("Nama fenomena", validators=[DataRequired()])
    content = TextAreaField ("Deskripsi", validators=[DataRequired()])
    type_of_event = SelectField(u"Fenomena",choices=[('Fase Bulan', 'Fase Bulan'),('Gerhana Matahari', 'Gerhana Matahari'), 
                                                         ('Gerhana Bulan','Gerhana Bulan' ), ('Komet', 'Komet'),
                                                         ('Hujan Meteor', 'Hujan Meteor'), ('Okultasi', 'Okultasi'),
                                                         ('Konjungsi Planet', 'Konjungsi Planet'), ('Equinox', 'Equinox'),
                                                         ('Solstice', 'Solstice')])
    start_date = DateField("Tanggal mulai",validators=[DataRequired()])
    end_date = DateField("Tanggal selesai",validators=[DataRequired()])
    sumber = TextAreaField ("Sumber", validators=[DataRequired()])
    lokasi = StringField ("Lokasi pengamatan", validators=[DataRequired()])
    submit = SubmitField ("Tambahkan fenomena ke kalender")    

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


#APP
#PROFIL
@app.route("/profil", methods=['GET', 'POST'])
def profil():
    mycursor.execute("SELECT * FROM users")
    users = mycursor.fetchall()
    mycursor.execute("SELECT * FROM contributors")
    contributors = mycursor.fetchall()
    mycursor.execute("SELECT * FROM consumers")
    consumers = mycursor.fetchall()
    return render_template("profil.html", users = users, contributors=contributors, consumers=consumers)

#AKUN PEMILIK WISATA


@app.route('/signup', methods=['GET', 'POST'])
def index():
    name = None
    form = UserForm()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users")
    users = mycursor.fetchall()
    if form.validate_on_submit():
        hashed_pw= bcrypt.hashpw(form.password_hash.data.encode('utf-8'), bcrypt.gensalt())
        query = "INSERT INTO users (name, username, email, nomor, deskripsi, password_hash, date_added) VALUES (%s, %s, %s, %s, %s, %s, TIMESTAMP(now()))"
        values = (form.name.data, form.username.data, form.email.data, form.nomor.data, form.deskripsi.data, hashed_pw)
        mycursor.execute(query, values)
        #mycursor.execute("INSERT INTO users (name, username, email, nomor, deskripsi, password_hash, date_added) VALUES (%s, %s, %s, %s, %s, %s, TIMESTAMP(now()))", (form.name.data, form.username.data, form.email.data, form.nomor.data, form.deskripsi.data, hashed_pw))
        mydb.commit()
        flash("Pengguna berhasil ditambahkan!")
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.username.data = ''
        form.password_hash = ''
    else:
         flash("Periksa apakah username memiliki spasi atau karakter yang tidak diperbolehkan!")
    return render_template('signup.html', form=form, name = name, users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    mycursor = mydb.cursor()
    #if request.method == 'POST':
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data.encode('utf-8')
        #username = request.form['username']
        #password = request.form['password'].encode('utf-8')
        mycursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        record = mycursor.fetchone()
        #mycursor.close()
        if record:
            if bcrypt.hashpw(password, record[7].encode('utf-8')) == record[7].encode('utf-8'):
            #mycursor.execute('SELECT password_hash FROM users WHERE username = %s;', (username,))
            #check = mycursor.fetchone()
            #if check_password_hash (record[7], form.password.data):

                session['loggedin'] = True
                session['username'] = record[2]
                session['id'] = record[0]
                #flash("Anda berhasil masuk!")
                if session['username'] == 'adminbebek':
                    return redirect ('/')
                else:
                    return redirect('/paket')
            else:
                flash("Kata sandi salah!")


        else:
            flash("Percobaan masuk gagal!")

    return render_template("login.html", form=form)

#AKUN KONSUMEN    
@app.route('/konsumen/signup', methods=['GET', 'POST'])
def signupkonsumen():
    name = None
    form = ConsumerForm()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM consumers")
    users = mycursor.fetchall()
    if form.validate_on_submit():
        hashed_pw= bcrypt.hashpw(form.password_hash.data.encode('utf-8'), bcrypt.gensalt())
        query = "INSERT INTO consumers (name, username, email, nomor, password_hash, title,  nationality, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s,  TIMESTAMP(now()))"
        values = (form.name.data, form.username.data, form.email.data, form.nomor.data, hashed_pw, form.title.data, form.nationality.data, )
        mycursor.execute(query, values)
        mydb.commit()
        flash("Pengguna berhasil ditambahkan!")
        
        
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.username.data = ''
        form.nomor.data = ''
        form.title.data = ''
        form.nationality.data = ''
        form.password_hash = ''
        
        
    else:
         flash("Periksa apakah username memiliki spasi atau karakter yang tidak diperbolehkan!")

    return render_template('signup konsumen.html', form=form, name = name, users=users)    

@app.route("/konsumen/login", methods=["GET", "POST"])
def loginkonsumen():
    form = LoginForm()
    mycursor = mydb.cursor()
    #if request.method == 'POST':
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data.encode('utf-8')
        mycursor.execute('SELECT * FROM consumers WHERE username = %s', (username,))
        record = mycursor.fetchone()

        if record:
            if bcrypt.hashpw(password, record[9].encode('utf-8')) == record[9].encode('utf-8'):

                session['loggedin'] = True
                session['username_k'] = record[3]
                session['id'] = record[0]
                #flash("Anda berhasil masuk!")
                return redirect('/')
            else:
                flash("Kata sandi salah!")

        else:
            flash("Percobaan masuk gagal!")

    return render_template("login konsumen.html", form=form)

#AKUN KONTRIBUTOR    
@app.route('/kontributor/signup', methods=['GET', 'POST'])
def signupkontributor():
    name = None
    form = ContributorsForm()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM contributors")
    users = mycursor.fetchall()
    if form.validate_on_submit():
        hashed_pw= bcrypt.hashpw(form.password_hash.data.encode('utf-8'), bcrypt.gensalt())
        uploaded_file = form.verification.data
        #grab image 1 name
        pic_filename = secure_filename(uploaded_file.filename)
        #set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #save image
        verification_path = os.path.join(app.config['VERIFICATION_FOLDER'], pic_name)
        uploaded_file.save(verification_path)
        post_1 = verification_path
        path_list = post_1.split('/')
        new_path = '/'.join(path_list)
        status = str('Belum diverifikasi')
        query = "INSERT INTO contributors (name, username, email, nomor, password_hash, verification, status, date_added) VALUES (%s, %s, %s, %s, %s, %s,%s,  TIMESTAMP(now()))"
        values = (form.name.data, form.username.data, form.email.data, form.nomor.data, hashed_pw, new_path, status)
        mycursor.execute(query, values)
        mydb.commit()
        
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.username.data = ''
        form.password_hash = ''
        
        flash("Account Successfully Requested!")
    else:
         flash("Periksa apakah username memiliki spasi atau karakter yang tidak diperbolehkan!")

    return render_template('signup kontributor.html', form=form, name = name, users=users)    

@app.route("/kontributor/login", methods=["GET", "POST"])
def loginkontributor():
    form = LoginForm()
    #mycursor = mydb.cursor()
    if form.validate_on_submit():
        #cek data
        username = form.username.data
        password = form.password.data.encode('utf-8')
        status = str('Belum diverifikasi')
        mycursor.execute('SELECT * FROM contributors WHERE username = %s AND status = %s ', (username, status))
        akun_none = mycursor.fetchone()
        mycursor.execute('SELECT * FROM contributors WHERE username = %s', (username,))
        akun = mycursor.fetchone()
        if akun_none: 
            #if akun[7] == None:
            flash("Akun belum diverfikasi!")
        elif bcrypt.hashpw(password, akun[5].encode('utf-8')) == akun[5].encode('utf-8'):
            session['loggedin'] = True
            session['username_c'] = akun[2]
            session['id'] = akun[0]
            flash("Anda berhasil masuk!")
            return redirect('/my_articles')
        else:
              flash("Kata sandi salah!")
    #else:
    #    flash("Percobaan masuk gagal! That user doesn't exist")
    
    return render_template("login kontributor.html", form=form)  

#BERANDA
@app.route('/', methods=['POST', 'GET'])
def beranda():
    mycursor.execute("SELECT * FROM posts ORDER BY date_posted")
    posts = mycursor.fetchall()
    mycursor.execute("SELECT * FROM transaction ORDER BY id")
    transactions = mycursor.fetchall()
    today = datetime.now()
    todaysdate = today.date()
    return render_template('beranda.html', transactions=transactions, posts=posts, todaysdate = todaysdate)


#ASTROWISATA
@app.route("/paket")
def post_saya():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM posts ORDER BY date_posted")
    posts = mycursor.fetchall()
    #posts = Posts.query.order_by(Posts.date_posted)
    return render_template("paket.html", posts = posts)
@app.route("/astrowisata")
def astrowisata():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM posts ORDER BY date_posted")
    posts = mycursor.fetchall()
    today = datetime.now()
    todaysdate = today.date()
    return render_template("astrowisata.html", posts = posts, todaysdate = todaysdate)    
#create post
@app.route("/create", methods=["GET", "POST"])
def create():
    form = PostForm()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM posts")
    posts = mycursor.fetchall()
    if form.validate_on_submit():
        author = session['id']
        author_uname = session['username']
        #image = form.image_1.data
        #image.save(image.filename)
        #image_binary = convertToBinaryData(image.filename)
        #uploaded image
        uploaded_file = form.image_1.data
        #grab image 1 name
        pic_filename = secure_filename(uploaded_file.filename)
        #set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #save image
        image_1_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
        uploaded_file.save(image_1_path)
        post_1 = image_1_path
        path_list = post_1.split('/')
        new_path = '/'.join(path_list)
        query = "INSERT INTO posts (title, content, location, event_date, event_end, type_of_event, price, image_1, author_id, author_username, date_posted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,TIMESTAMP(now()))"
        values = (form.title.data, form.content.data, form.location.data, form.event_date.data, form.event_end.data,form.type_of_event.data, form.price.data, new_path, author, author_uname)
        mycursor.execute(query, values)
        mydb.commit()
        #clear the form
        form.title.data = ''
        form.content.data = ''
        form.location.data = ''
        form.event_date.data = ''
        form.event_end.data = ''
        form.type_of_event.data = ''
        form.price.data = ''
        
        flash("Paket berhasil dibuat!")
        return redirect('/paket')
    return render_template("create.html", form=form)    
    
@app.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    mycursor = mydb.cursor()
    post_q = "SELECT * FROM posts WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post = mycursor.fetchone()
    form = CartForm()
    today = datetime.now()
    todaysdate = today.date()
    mycursor.execute('SELECT * FROM users WHERE username = %s', (post[4],))
    record2 = mycursor.fetchone()
    nomor = record2[5]
    email = record2[3]
    if form.validate_on_submit():
        consumer = session['id']
        username = session['username_k']
        id_input = id
        title = post[1]
        price = post[10]
        status = str("Belum dibayar")
        total_price = price*form.quantity.data
        query = "INSERT INTO transaction (quantity, title, price, consumer_id, post_id, total_price, status, start_date, end_date, consumer_username) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
        values = (form.quantity.data, title, price, consumer, id, total_price, status, form.start_date.data,form.end_date.data, username)
        mycursor.execute(query, values)
        mydb.commit()
        form.quantity.data = ''
        form.start_date.data = ''
        form.end_date.data = ''
        return redirect('/mycart')
        
    return render_template("post.html", post=post, form=form, todaysdate = todaysdate, nomor = nomor, email = email)

@app.route("/post/edit/<int:id>", methods=['GET', 'POST'])
#@login_required
def edit_post(id):
    post_q = "SELECT * FROM posts WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post= mycursor.fetchone()
    form = PostForm()
    if form.validate_on_submit():
        if form.image_1.data == None:
            query = "UPDATE posts SET title = %s, content = %s, location = %s, event_date = %s, event_end = %s, type_of_event = %s, price = %s WHERE id = %s"
            values = (form.title.data, form.content.data, form.location.data, form.event_date.data, form.event_end.data, form.type_of_event.data, form.price.data, id)
            mycursor.execute(query, values)
            mydb.commit()
            flash("Paket berhasil diubah!")
            return redirect(url_for('post', id = post[0] )) 
        else:
            
            uploaded_file = form.image_1.data
            #grab image 1 name
            pic_filename = secure_filename(uploaded_file.filename)
            #set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            #save image
            image_1_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
            uploaded_file.save(image_1_path)
            post_1 = image_1_path
            path_list = post_1.split('/')
            new_path = '/'.join(path_list)
            query = "UPDATE posts SET title = %s, content = %s, location = %s, event_date = %s, event_end = %s, type_of_event = %s, price = %s, image_1 = %s WHERE id = %s"
            values = (form.title.data, form.content.data, form.location.data, form.event_date.data, form.event_end.data, form.type_of_event.data, form.price.data, new_path, id)
            mycursor.execute(query, values)
            mydb.commit()
            
            flash("Paket berhasil diubah!")
            return redirect(url_for('post', id = post[0] )) 
        
    form.title.data = post[1]
    form.content.data = post[2]
    form.location.data = post[6]
    form.event_date.data = post[5]
    form.type_of_event.data = post[7]
    form.price.data = post[10]
    form.event_end.data = post[12]
    form.image_1.data = post[9]
    
    return render_template("edit.html", form=form)

 
@app.route("/post/delete/<int:id>")
#@login_required
def delete_post(id):
    post_q = "SELECT * FROM posts WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post_to_delete = mycursor.fetchone()
    user_id = session['id']
    if user_id == post_to_delete[3]:
        try:
            delete = "DELETE FROM posts WHERE id = %s LIMIT 1"
            mycursor.execute(delete, id_input)
            mydb.commit()
            flash ("Post deleted!")
            
            #posts = Posts.query.order_by(Posts.date_posted)
            return redirect("/paket")
        except:
            flash ("Ada masalah dalam penghapusan!")
            mycursor.execute("SELECT * FROM posts ORDER BY date_posted")
            posts = mycursor.fetchall()
            return render_template("paket.html", posts = posts)
        
    else:
        flash ("Anda tidak memiliki akses!")
        mycursor.execute("SELECT * FROM posts ORDER BY date_posted")
        posts = mycursor.fetchall()
        return render_template("paket.html", posts = posts) 

#mycart
@app.route('/mycart')
def my_cart():
    mycursor.execute("SELECT * FROM transaction ORDER BY id")
    transactions = mycursor.fetchall()
    today = datetime.now()
    todaysdate = today.date()
    return render_template("mycart.html", transactions = transactions, todaysdate = todaysdate)

@app.route("/mycart/edit/<int:id>", methods=['GET', 'POST'])
def edit_transaction(id):
    transaction_q = "SELECT * FROM transaction WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(transaction_q, id_input)
    transaction = mycursor.fetchone()
    form = CartForm()
    if form.validate_on_submit(): 
        total_price = transaction[5]*form.quantity.data
        query = "UPDATE transaction SET quantity = %s, total_price = %s WHERE id = %s"
        values = (form.quantity.data, total_price, id)
        mycursor.execute(query, values)
        mydb.commit()
        
        flash("Transaction successfully edited!")
        return redirect(url_for('my_cart'))
     
    form.quantity.data = transaction[3]
    form.start_date.data = transaction[9]
    form.end_date.data = transaction[10]
        
    return render_template("editcart.html", form=form, transaction=transaction)


@app.route("/mycart/delete/<int:id>")
def delete_transaction(id):
    transaction_q = "SELECT * FROM transaction WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(transaction_q, id_input)
    transaction_to_delete = mycursor.fetchone()
    user_id = session['id']
    if user_id == transaction_to_delete[1]:
        try:
            delete = "DELETE FROM transaction WHERE id = %s LIMIT 1"
            mycursor.execute(delete, id_input)
            mydb.commit()
            flash ("Item deleted!")
            
            return redirect("/mycart")
        except:
            flash ("Ada masalah dalam penghapusan!")
            mycursor.execute("SELECT * FROM transaction ORDER BY id")
            transactions = mycursor.fetchall()
            return render_template("mycart.html", transactions = transactions)

@app.route('/mycart/checkout/<int:id>', methods=['GET', 'POST'])
def checkout(id):
    transaction_q = "SELECT * FROM transaction WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(transaction_q, id_input)
    transaction = mycursor.fetchone()
    consumer_id = transaction[1]
    form = CheckoutForm()
    if form.validate_on_submit(): 
    
        uploaded_file = form.payment.data
        #grab image  name
        pic_filename = secure_filename(uploaded_file.filename)
        #set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #save image
        payment_path = os.path.join(app.config['PAYMENT_FOLDER'], pic_name)
        uploaded_file.save(payment_path)
        transaction_payment = payment_path
        path_list = transaction_payment.split('/')
        new_path = '/'.join(path_list)
        status = str("Dalam proses")
        query = "UPDATE transaction SET status = %s, payment= %s WHERE id = %s"
        values = (status, new_path, id)
        mycursor.execute(query, values)
        query2 = "UPDATE consumers SET identity_num = %s, dob = %s WHERE id = %s"
        values2 = (form.identity_num.data, form.dob.data, consumer_id)
        mycursor.execute(query2, values2)
        mydb.commit()
        
        return redirect(url_for('my_cart'))
    form.payment.data = ''
    return render_template("checkout.html", form= form, transaction = transaction) 

#rateandreview
@app.route("/mycart/rateandreview/<int:id>", methods=['GET', 'POST'])
def rate(id):
    transaction_q = "SELECT * FROM transaction WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(transaction_q, id_input)
    transaction = mycursor.fetchone()
    today = datetime.now()
    todaysdate = today.date()
    form = RateForm()
    if form.validate_on_submit(): 
        status = str("Selesai")
        query = "UPDATE transaction SET status = %s, rate= %s, review= %s WHERE id = %s"
        values = (status, form.rate.data, form.review.data, id)
        mycursor.execute(query, values)
        mydb.commit()
        post_id = transaction[2]
        query2 = "SELECT rate FROM transaction WHERE post_id = %s"
        value = (post_id,)
        mycursor.execute(query2, value)
        result = mycursor.fetchall()
        average_amount = np.mean(result)
        query3 = "UPDATE posts SET average = %s WHERE id = %s"
        values3 = (average_amount, post_id)
        mycursor.execute(query3, values3)
        mydb.commit()
        return redirect(url_for('my_cart'))
        
    return render_template("rateandreview.html", form=form, transaction=transaction, todaysdate = todaysdate)

@app.route("/rateandreview")
#@login_required
def rr():
    mycursor.execute("SELECT * FROM posts ORDER BY date_posted")
    posts = mycursor.fetchall()
    return render_template("ratereview.html", posts = posts)

@app.route("/rateandreview/post/<int:id>", methods=['GET', 'POST'])
#@login_required
def ratereview(id):
    post_q = "SELECT * FROM posts WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post = mycursor.fetchone()
    transaction_q = "SELECT * FROM transaction WHERE post_id = %s AND rate != 0" 
    values = (id,)
    mycursor.execute(transaction_q, values)
    transaction = mycursor.fetchall()
    
    return render_template("postrateandreview.html", transaction=transaction, post=post)
    


#TRIP


@app.route("/endtrip")
def triplogs():
    username = session['username']
    query = "SELECT * FROM posts WHERE author_username = %s"
    value = (username,)
    mycursor.execute(query, value)
    posts = mycursor.fetchall()
    today = datetime.now()
    todaysdate = today.date()
    transactions_list = []
    for p in posts:
        query2 = "SELECT * FROM transaction WHERE post_id = %s"
        value2 = (p[0],)
        mycursor.execute(query2, value2)
        transactions = mycursor.fetchall()
        for transaction in transactions:
            transactions_list.append(transaction)
    

    return render_template("triplogs.html", transactions = transactions_list, todaysdate = todaysdate )

    
@app.route('/endtrip/<int:id>')
def endtrip(id):
    status = str("Perjalanan selesai")
    post_q = "UPDATE transaction SET status = %s WHERE id = %s" 
    values = (status,id)
    mycursor.execute(post_q, values)
    mydb.commit()
    return redirect("/endtrip")  
  
    
#ADMINPAGE
@app.route('/adminpage/transactions')
#@login_required
def admin():
    mycursor.execute("SELECT * FROM transaction ORDER BY id")
    transactions = mycursor.fetchall()
    return render_template("adminpage.html", transactions = transactions)

@app.route('/verification/<int:id>')
def ver(id):
    status = str("Sudah bayar")
    post_q = "UPDATE transaction SET status = %s WHERE id = %s" 
    values = (status,id)
    mycursor.execute(post_q, values)
    mydb.commit()
    return redirect("/adminpage/transactions")

@app.route('/notverified/<int:id>')
def not_ver(id):
    status = str("Bukti pembayaran tidak sesuai. Coba lagi")
    post_q = "UPDATE transaction SET status = %s WHERE id = %s" 
    values = (status,id)
    mycursor.execute(post_q, values)
    mydb.commit()
    return redirect("/adminpage/transactions")    
    
@app.route('/adminpage/contributor_verification')

def contributor_list():
    mycursor.execute("SELECT * FROM contributors")
    contributors = mycursor.fetchall()   
    return render_template("contributorslist.html", contributors = contributors)

@app.route('/contributor_verification/<int:id>')
def ver2(id):
    status = str("Sudah diverifikasi")
    post_q = "UPDATE contributors SET status = %s WHERE id = %s" 
    values = (status,id)
    mycursor.execute(post_q, values)
    mydb.commit()
    return redirect("/adminpage/contributor_verification")

@app.route("/adminpage/delete/<int:id>")
#@login_required
def delete_contributor(id):
    contributor_q = "SELECT * FROM contributors WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(contributor_q, id_input)
    account_to_delete = mycursor.fetchone()
    try:
        delete = "DELETE FROM contributors WHERE id = %s  LIMIT 1"
        id_input = (id,)
        mycursor.execute(delete, id_input)
        mydb.commit()
        flash ("Akun berhasil dihapus!")
            
        return redirect("/adminpage/contributor_verification")
    except:
        flash ("Ada masalah dalam penghapusan!")
        mycursor.execute("SELECT * FROM contributors ORDER BY id")
        contributors = mycursor.fetchall()
        return render_template("contributorslist.html", contributors = contributors)



@app.route('/adminpage/users')
#@login_required
def user_list():
    mycursor.execute("SELECT * FROM users")
    users = mycursor.fetchall()
    return render_template("users_list.html", users = users)



@app.route('/adminpage/consumers')
#@login_required
def consumer_list():
    mycursor.execute("SELECT * FROM consumers")
    users = mycursor.fetchall()
    return render_template("consumers_list.html", users = users)
 
 
@app.route('/adminpage/articles')
#@login_required
def articles_list():
    mycursor.execute("SELECT * FROM articles")
    posts = mycursor.fetchall()
    return render_template("articles_list.html", posts = posts)
    
@app.route('/articles_verification/<int:id>')
def artikel_ver(id):
    status = str("Sudah diverifikasi")
    post_q = "UPDATE articles SET status = %s WHERE id = %s" 
    values = (status,id)
    mycursor.execute(post_q, values)
    mydb.commit()
    return redirect("/adminpage/articles")
    
@app.route('/articles_notverified/<int:id>')
def artikel_notver(id):
    status = str("Verifikasi ulang")
    post_q = "UPDATE articles SET status = %s WHERE id = %s" 
    values = (status,id)
    mycursor.execute(post_q, values)
    mydb.commit()
    return redirect("/adminpage/articles")    

@app.route("/adminpage/articles/delete/<int:id>")
#@login_required
def delete_article(id):
    try:
        delete_articles = "DELETE FROM articles WHERE id = %s"
        mycursor.execute(delete_articles, id)
        mydb.commit()
        flash ("Artikel berhasil dihapus!")
            
        return redirect("/adminpage/articles")
        
    except:
        flash ("Ada masalah dalam penghapusan!")
        mycursor.execute("SELECT * FROM articles ORDER BY date_posted")
        article = mycursor.fetchall()
        return render_template("articles_list.html", article = article)

 
@app.route('/adminpage/calendar/add', methods=['GET', 'POST'])
#@login_required
def cal_admin():
    form = EventForm()
    if form.validate_on_submit():
        query = "INSERT INTO events (title, content, lokasi, start_date, end_date, type_of_event, sumber) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (form.title.data, form.content.data, form.lokasi.data, form.start_date.data, form.end_date.data,form.type_of_event.data, form.sumber.data)
        mycursor.execute(query, values)
        mydb.commit()
        #clear the form
        form.title.data = ''
        form.content.data = ''
        form.lokasi.data = ''
        form.start_date.data = ''
        form.end_date.data = ''
        form.type_of_event.data = ''
        form.sumber.data = ''
        flash("Fenomena berhasil ditambahkan!")
    return render_template("admincal.html", form = form) 

@app.route('/adminpage/calendar', methods=['GET', 'POST'])
#@login_required
def cal_list():
    mycursor.execute("SELECT * FROM events")
    events  = mycursor.fetchall()
    return render_template("admincal_list.html", events = events) 

@app.route('/adminpage/calendar/edit/<int:id>', methods=['GET', 'POST'])
#@login_required
def cal_admin_edit(id):
    event_q = "SELECT * FROM events WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(event_q, id_input)
    event = mycursor.fetchone()
    form = EventForm()
    if form.validate_on_submit():
        query = "UPDATE transaction SET title = %s, content= %s, start_date= %s, end_date = %s, type_of_event = %s, sumber = %s, lokasi = %s WHERE id = %s"
        values = (form.title.data, form.content.data, form.start_date.data, form.end_date.data, form.type_of_event.data, form.sumber.data, form.lokasi.data, id)
        mycursor.execute(query, values)
        mydb.commit()
        flash("Fenomena berhasil diubah")
        return redirect(url_for('cal_list'))
    form.title.data = event[1]
    form.content.data = event[2]
    form.start_date.data = event[4]
    form.end_date.data = event[5]
    form.type_of_event.data = event[3]
    form.lokasi.data = event[7]
    form.sumber.data = event[6]
    return render_template("admincal_edit.html", form = form, event=event)
 
@app.route("/adminpage/calendar/delete/<int:id>")
def cal_delete(id):
    event_q = "SELECT * FROM events WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(event_q, id_input)
    event_to_delete = mycursor.fetchone()
    try:
        delete = "DELETE FROM events WHERE id = %s LIMIT 1"
        mycursor.execute(delete, id_input)
        mydb.commit()
        flash ("Fenomena berhasil dihapus!")
            
        return redirect("/adminpage/calendar")
    except:
        flash ("Ada masalah dalam penghapusan!")
        mycursor.execute("SELECT * FROM events ORDER BY id")
        events = mycursor.fetchall()
        return render_template("admincal_list.html", events = events)
    
        
#search bar
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Search")

@app.context_processor 
def base():
    form = SearchForm()
    return dict(form = form)

@app.route("/search", methods=['POST'])
def search():
    form = SearchForm()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM posts")
    posts = mycursor.fetchall()
    today = datetime.now()
    todaysdate = today.date()
    if form.validate_on_submit():
        post.searched = form.searched.data
        query = "SELECT * FROM posts WHERE title LIKE %s OR location LIKE %s OR type_of_event LIKE %s"
        mycursor.execute(query, ('%' + post.searched + '%', '%' + post.searched + '%', '%' + post.searched + '%',))
        posts =  mycursor.fetchall()
        return render_template("search.html", form=form, searched = post.searched, posts= posts, todaysdate = todaysdate)        

@app.route("/artikel/search", methods=['POST'])
def search_artikel():
    form = SearchForm()
    mycursor.execute("SELECT * FROM articles")
    posts = mycursor.fetchall()
    if form.validate_on_submit():
        post.searched = form.searched.data
        query = "SELECT * FROM articles WHERE title LIKE %s"
        mycursor.execute(query, ('%' + post.searched + '%',))
        posts =  mycursor.fetchall()
        return render_template("search_artikel.html", form=form, searched = post.searched, posts =posts) 
 
#filter
        
@app.route("/astrowisata/filter", methods=['POST'])
def searchfilters():
    mycursor.execute("SELECT * FROM posts")
    posts = mycursor.fetchall()
    today = datetime.now()
    todaysdate = today.date()
    if request.method == "POST":
        pricerange = request.form["pricerange"]
        filtertype = request.form["filtertype"]
        if filtertype == "None" :
            if pricerange == "0":
                query = "SELECT * FROM posts WHERE price between '0' AND '99999'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "1":
                query = "SELECT * FROM posts WHERE price between '100000' AND '499999'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate) 
            if pricerange == "2":
                query = "SELECT * FROM posts WHERE price between '500000' AND '999999'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()               
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "3":
                query = "SELECT * FROM posts WHERE price between '1000000' AND '1999999'"
                mycursor.execute(query)
                posts =  mycursor.fetchall() 
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "4":
                query = "SELECT * FROM posts WHERE price between '2000000' AND '2999999'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()                 
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "5":
                query = "SELECT * FROM posts WHERE price between '3000000' AND '3999999'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()                  
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "6":
                query = "SELECT * FROM posts WHERE price between '4000000' AND '5000000'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()                   
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "7":
                query = "SELECT * FROM posts WHERE price > '5000000'"
                mycursor.execute(query)
                posts =  mycursor.fetchall()                   
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
        elif pricerange == "None":
            query = "SELECT * FROM posts WHERE type_of_event LIKE %s"
            mycursor.execute(query, ('%' + filtertype + '%',))
            posts =  mycursor.fetchall()
            return render_template("filtered.html", posts =posts, todaysdate = todaysdate)    
        else:
            if pricerange == "0":
                query = "SELECT * FROM posts WHERE price between '0' AND '99999' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "1":
                query = "SELECT * FROM posts WHERE price between '100000' AND '499999' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "2":
                query = "SELECT * FROM posts WHERE price between '500000' AND '999999' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "3":
                query = "SELECT * FROM posts WHERE price between '1000000' AND '1999999' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "4":
                query = "SELECT * FROM posts WHERE price between '2000000' AND '2999999' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "5":
                query = "SELECT * FROM posts WHERE price between '3000000' AND '3999999' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "6":
                query = "SELECT * FROM posts WHERE price between '4000000' AND '5000000' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
            if pricerange == "7":
                query = "SELECT * FROM posts WHERE price > '5000000' AND type_of_event LIKE %s"
                mycursor.execute(query, ('%' + filtertype + '%',))
                posts =  mycursor.fetchall()
                return render_template("filtered.html",  posts =posts, todaysdate = todaysdate)  
                
                
@app.route("/artikel/filter", methods=['POST'])
def articlesfilters():
    mycursor.execute("SELECT * FROM articles")
    posts = mycursor.fetchall()
    if request.method == "POST":
        filtertype = request.form["filtertype"]
        query = "SELECT * FROM articles WHERE type LIKE %s"
        mycursor.execute(query, ('%' + filtertype + '%',))
        posts =  mycursor.fetchall()
        return render_template("filteredarticles.html", posts =posts)    
        
                
#articles
@app.route("/my_articles")
def artikel_saya():
    mycursor.execute("SELECT * FROM articles ORDER BY date_posted")
    posts = mycursor.fetchall()
    return render_template("my_articles.html", posts = posts)

@app.route("/artikel")
def artikel():
    mycursor.execute("SELECT * FROM articles ORDER BY date_posted")
    posts = mycursor.fetchall()
    return render_template("articles.html", posts = posts)
    
@app.route("/create_articles", methods=["GET", "POST"])
def create_articles():
    form = ArticleForm()
    if form.validate_on_submit():
        author = session['id']
        author_uname = session['username_c']
        #uploaded image
        uploaded_file = form.image_1.data
        #grab image 1 name
        pic_filename = secure_filename(uploaded_file.filename)
        #set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #save image
        image_1_path = os.path.join(app.config['IMAGES_FOLDER'], pic_name)
        uploaded_file.save(image_1_path)
        post_1 = image_1_path
        path_list = post_1.split('/')
        new_path = '/'.join(path_list)
        
        #uploaded image
        uploaded_file2 = form.verification.data
        pic_filename2 = secure_filename(uploaded_file2.filename)
        pic_name2 = str(uuid.uuid1()) + "_" + pic_filename2
        #save image
        verification_path = os.path.join(app.config['PROOF_FOLDER'], pic_name2)
        uploaded_file2.save(verification_path)
        post_2 = verification_path
        path_list2 = post_2.split('/')
        new_path2 = '/'.join(path_list2)
        
        status = str("Menunggu persetujuan")
        if form.link.data == None:
        
            query = "INSERT INTO articles (title, content, image, verification_proof, status, author_id, author_username, type, date_posted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TIMESTAMP(now()))"
            values = (form.title.data, form.content.data, new_path, new_path2, status, author, author_uname, form.article_type.data)
            mycursor.execute(query, values)
            mydb.commit()
            #clear the form
            form.title.data = ''
            form.content.data = ''
            
            flash("Artikel berhasil ditambahkan!")
            return redirect(url_for('artikel_saya')) 
        else:
            query = "INSERT INTO articles (title, content, image, verification_proof, status, author_id, author_username, link, type, date_posted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TIMESTAMP(now()))"
            values = (form.title.data, form.content.data, new_path, new_path2, status, author, author_uname, form.link.data, form.article_type.data)
            mycursor.execute(query, values)
            mydb.commit()
            #clear the form
            form.title.data = ''
            form.content.data = ''
            
            flash("Artikel berhasil ditambahkan!")
            return redirect(url_for('artikel_saya')) 
    return render_template("createarticles.html", form=form)  

@app.route("/articles/<int:id>", methods=["GET", "POST"])
def articles(id):
    post_q = "SELECT * FROM articles WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post= mycursor.fetchone()
    user_id = post[3]
    query = "SELECT * FROM contributors WHERE id = %s"
    value = (user_id,)
    mycursor.execute(query, value)
    contributor = mycursor.fetchone()
    name = contributor[1]
    return render_template("artikel.html", post=post, name = name)    


    

@app.route("/articles/edit/<int:id>", methods=['GET', 'POST'])
def edit_articles(id):
    post_q = "SELECT * FROM articles WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post= mycursor.fetchone()
    form = ArticleForm()
    if form.validate_on_submit():
        if form.image_1.data == None and form.verification.data == None:
            query = "UPDATE articles SET title = %s, content = %s, type = %s WHERE id = %s"
            values = (form.title.data, form.content.data, form.article_type.data, id)
            mycursor.execute(query, values)
            mydb.commit()
            flash("Artikel berhasil diubah!")
            return redirect(url_for('articles', id = post[0] )) 
        elif form.verification.data == None:
            uploaded_file = form.image_1.data
            #grab image 1 name
            pic_filename = secure_filename(uploaded_file.filename)
            #set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            #save image
            image_1_path = os.path.join(app.config['IMAGES_FOLDER'], pic_name)
            uploaded_file.save(image_1_path)
            post_1 = image_1_path
            path_list = post_1.split('/')
            new_path = '/'.join(path_list)
    
            
            query2 = "UPDATE articles SET title = %s, content = %s, image = %s type = %s WHERE id = %s"
            values2 = (form.title.data, form.content.data, new_path, form.article_type.data, id)
            mycursor.execute(query2, values2)
            mydb.commit()
            
            flash("Artikel berhasil diubah!")
            return redirect(url_for('articles', id = post[0] )) 
            
    form.title.data = post[1]
    form.content.data = post[2]
    form.image_1.data = post[6]
    return render_template("edit_artikel.html", form=form)

@app.route("/articles/delete/<int:id>")
def delete_articles(id):
    post_q = "SELECT * FROM articles WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    post_to_delete = mycursor.fetchone()
    user_id = session['id']
    if user_id == post_to_delete[3]:
        try:
            delete = "DELETE FROM articles WHERE id = %s"
            mycursor.execute(delete, id_input)
            mydb.commit()
            flash ("Post deleted!")
        
            return redirect("/my_articles")
        except:
            flash ("Ada masalah dalam penghapusan!")
            mycursor.execute("SELECT * FROM articles ORDER BY date_posted")
            posts = mycursor.fetchall()
            return render_template("my_articles.html", posts = posts)
        
    else:
        flash ("Anda tidak memiliki akses!")
        mycursor.execute("SELECT * FROM articles ORDER BY date_posted")
        posts = mycursor.fetchall()
        return render_template("articles.html", posts = posts) 
    
#calendar
@app.route("/kalenderastronomi")
def cal():
    mycursor.execute("SELECT * FROM posts ORDER BY event_date")
    allevents = mycursor.fetchall()
    mycursor.execute("SELECT * FROM events ORDER BY id")
    otherevents = mycursor.fetchall()
    date_1 = timedelta(days=1)
    today = datetime.now()
    todaysdate = today.date()
    return render_template("kalender.html", events=allevents, date_1=date_1, otherevents = otherevents, todaysdate=todaysdate)

@app.route("/kalenderastronomi/event/<int:id>", methods=['GET', 'POST'])
def description(id):
    post_q = "SELECT * FROM events WHERE id = %s" 
    id_input = (id,)
    mycursor.execute(post_q, id_input)
    event = mycursor.fetchone()
    return render_template("fenomena.html", event = event)

#simulasi
@app.route("/simulasi")
def simulasi():
    return render_template("simulasi.html")

@app.route("/simulasi/fasebulan")
def fasebulan():
    return render_template("lunarsimulator.html")

@app.route("/simulasi/bintangganda")
def bintangganda():
    return render_template("eclipsingbinary.html")

@app.route("/simulasi/matahari_bulan_bumi")
def sunmoonearth():
    return render_template("sunmoonearth.html")

                
#logout route
@app.route("/logout")
def logout():
    #logout_user()
    session.pop('loggedin', None)
    #session.pop('username_c', None)
    #session.pop('username', None)
    #session.pop('username_k', None)
    session.clear()
    flash("Anda sudah keluar dari akun!")
    return redirect("/")   


@app.route("/underconstruction")
def unavailable():            
    return render_template("underconstruction.html")  


if __name__ == '__main__':
    app.run(debug=True)
