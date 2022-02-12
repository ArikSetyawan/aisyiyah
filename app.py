from flask import Flask, render_template, session, redirect, url_for, request
from peewee import *
import time, datetime, string, os, random

db = "aisyiyah.db"
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta():
		database=database

class user(BaseModel):
	id = AutoField(primary_key=True)
	level = IntegerField() #Admin = 1, teacher = 2, student=3
	email = CharField(unique=True)
	password = CharField()

class student(BaseModel):
	id = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	nama = CharField()
	kelamin = CharField()
	photo = CharField(default='default.png')

class teacher(BaseModel):
	id = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	nama = CharField()
	kelamin = CharField()
	photo = CharField(default='default.png')

class conseling(BaseModel):
	id = AutoField()
	user_ask = ForeignKeyField(user)
	title = CharField()
	question = TextField()
	user_answer = ForeignKeyField(user, null=True, default=None)
	answer = TextField(null=True, default=None)
	answered = BooleanField(default=False)
	dateask = IntegerField()
	dateask_print = CharField()
	dateans = IntegerField(null=True,default=None)
	dateans_print = CharField(null=True,default=None)

def create_tables():
	with database:
		database.create_tables([user, student, teacher, conseling])

app = Flask(__name__)
app.secret_key = "Thisisverysecret"
app.config['folderimage'] = 'static/image'

# Global Variable
ALLOWED_EXTENDSION = set(['png','jpeg','jpg'])

# custom function
def upload_image(file,id_user,level):
	if file.filename == '':
		return 'fail'
	
	if not '.' in file.filename and file.filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENDSION:
		return 'fail'
	
	filename = 'Aisyiyah-'+''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))
	extendsion = '.'+file.filename.rsplit('.',1)[1].lower()
	filename = str(filename)+str(extendsion)

	if level == 2:
		# get_teacher
		get_teacher = teacher.get(teacher.id_user == id_user)
		if get_teacher.photo == "default.png":
			update_teacher = teacher.update(photo=filename).where(teacher.id_user == id_user)
			update_teacher.execute()
			file.save(os.path.join(app.config['folderimage'],filename))
			return filename
		else:
			os.remove(os.path.join(app.config['folderimage'],get_teacher.photo))
			update_teacher = teacher.update(photo=filename).where(teacher.id_user == id_user)
			update_teacher.execute()
			file.save(os.path.join(app.config['folderimage'],filename))
			return filename
	else:
		# get_student
		get_student = student.get(student.id_user == id_user)
		if get_student.photo == "default.png":
			update_student = student.update(photo=filename).where(student.id_user == id_user)
			update_student.execute()
			file.save(os.path.join(app.config['folderimage'],filename))
			return filename
		else:
			os.remove(os.path.join(app.config['folderimage'],get_student.photo))
			update_student = student.update(photo=filename).where(student.id_user == id_user)
			update_student.execute()
			file.save(os.path.join(app.config['folderimage'],filename))
			return filename
	
def cek_user(id_user):
	cek = user.select().where(user.id == id_user)
	if cek.exists():
		return True
	else:
		return False

@app.route('/')
def index():
	data_teacher = teacher.select()
	return render_template('index.html',data_teacher=data_teacher)

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/login',methods=['GET','POST'])
def login():
	if 'login' in session:
		return redirect(url_for('index'))
	else:
		if request.method == 'GET':
			return render_template('login.html')
		else:
			email = request.form['email']
			password = request.form['password']
			# cek
			cek_user = user.select().where((user.email==email)&(user.password==password))
			if cek_user.exists():
				cek_user = cek_user.get()
				session['login'] = True
				session['id_user'] = cek_user.id
				session['user'] = cek_user.email
				session['level'] = cek_user.level
				if cek_user.level == 2:
					get_teacher = teacher.get(teacher.id_user == cek_user.id)
					session['photo'] = get_teacher.photo
					return redirect(url_for('dashboard'))
				elif cek_user.level == 3:
					get_student = student.get(student.id_user == cek_user.id)
					session['photo'] = get_student.photo
					return redirect(url_for('dashboard'))
				else:
					return redirect(url_for('dashboard'))
			else:
				return redirect(url_for('login'))

@app.route('/registration', methods=['GET','POST'])
def registration():
	if 'login' in session:
		return redirect(url_for('index'))
	else:
		if request.method == 'GET':
			return render_template('registration.html')
		else:
			nama = request.form['nama']
			kelamin = request.form['jk']
			email = str(request.form['email']).lower()
			password = request.form['password']
			# cek if email exists:
			cek_email = user.select().where(user.email == email)
			if cek_email.exists():
				return redirect(url_for('users'))
			else:
				# insert_user
				user.create(level=3,email=email,password=password)
				# get_user
				get_user = user.get(user.email==email)
				student.create(id_user=get_user.id, nama=nama,kelamin=kelamin)
				return redirect(url_for('login'))
	
@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route('/users')
def users():
	if 'login' in session:
		if session['level'] == 1:
			get_student = student.select()
			get_teacher = teacher.select()
			return render_template('users.html',student=get_student,teacher=get_teacher)
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/addteacher',methods=['POST'])
def addteacher():
	if 'login' in session:
		if session['level'] == 1:
			nama = request.form['nama']
			kelamin = request.form['jk']
			email = str(request.form['email']).lower()
			password = request.form['password']
			# cek if email exists:
			cek_email = user.select().where(user.email == email)
			if cek_email.exists():
				return redirect(url_for('users'))
			else:
				# insert_user
				user.create(level=2,email=email,password=password)
				# get_user
				get_user = user.get(user.email==email)
				teacher.create(id_user=get_user.id, nama=nama,kelamin=kelamin)
				return redirect(url_for('users'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/edit-teacher/<id_user>',methods=['POST'])
def editteacher(id_user):
	if 'login' in session:
		if session['level'] == 1:
			nama = request.form['nama']
			kelamin = request.form['jk']
			email = str(request.form['email']).lower()
			password = request.form['password']
			
			#cek user
			cek_user = user.select().where(user.id == id_user)
			if cek_user.exists():
				cek_email = user.select().where(user.email == email)
				if cek_email.exists():
					cek_email = cek_email.get()
					if int(cek_email.id) == int(id_user):
						update_user = user.update(email=email,password=password).where(user.id == id_user)
						update_teacher = teacher.update(nama=nama,kelamin=kelamin).where(teacher.id_user == id_user)
						update_user.execute()
						update_teacher.execute()
						return redirect(url_for('users'))
					else:
						return redirect(url_for('users'))
				else:
					update_user = user.update(email=email,password=password).where(user.id == id_user)
					update_teacher = teacher.update(nama=nama,kelamin=kelamin).where(teacher.id_user == id_user)
					update_user.execute()
					update_teacher.execute()
					return redirect(url_for('users'))
			else:
				return redirect(url_for('users'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/addstudent',methods=['POST'])
def addstudent():
	if 'login' in session:
		if session['level'] == 1:
			nama = request.form['nama']
			kelamin = request.form['jk']
			email = str(request.form['email']).lower()
			password = request.form['password']
			# cek if email exists:
			cek_email = user.select().where(user.email == email)
			if cek_email.exists():
				return redirect(url_for('registration'))
			else:
				# insert_user
				user.create(level=3,email=email,password=password)
				# get_user
				get_user = user.get(user.email==email)
				student.create(id_user=get_user.id, nama=nama,kelamin=kelamin)
				return redirect(url_for('users'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/edit-student/<id_user>',methods=['POST'])
def editstudent(id_user):
	if 'login' in session:
		if session['level'] == 1:
			nama = request.form['nama']
			kelamin = request.form['jk']
			email = str(request.form['email']).lower()
			password = request.form['password']
			
			#cek user
			cek_user = user.select().where(user.id == id_user)
			if cek_user.exists():
				cek_email = user.select().where(user.email == email)
				if cek_email.exists():
					cek_email = cek_email.get()
					if int(cek_email.id) == int(id_user):
						update_user = user.update(email=email,password=password).where(user.id == id_user)
						update_student = student.update(nama=nama,kelamin=kelamin).where(student.id_user == id_user)
						update_user.execute()
						update_student.execute()
						return redirect(url_for('users'))
					else:
						return redirect(url_for('users'))
				else:
					update_user = user.update(email=email,password=password).where(user.id == id_user)
					update_student = student.update(nama=nama,kelamin=kelamin).where(student.id_user == id_user)
					update_user.execute()
					update_student.execute()
					return redirect(url_for('users'))
			else:
				return redirect(url_for('users'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/delete-user/<id_user>')
def deleteuser(id_user):
	if 'login' in session:
		if session['level'] == 1:
			# get use
			get_user = user.select().where(user.id == id_user)
			if get_user.exists():
				get_user = get_user.get()
				if get_user.level == 2:
					# get_teacher
					get_teacher = teacher.get(teacher.id_user == id_user)
					if get_teacher.photo != 'default.png':
						# remove photo
						os.remove(os.path.join(app.config['folderimage'],get_teacher.photo))
					# delete teacher
					delete_teacher = teacher.delete().where(teacher.id_user == id_user)
					delete_teacher.execute()
					# delete related conseling
					del_conseling = conseling.delete().where(conseling.user_answer == id_user)
					del_conseling.execute()
					# delete user
					delete_user = user.delete().where(user.id == id_user)
					delete_user.execute()
					return redirect(url_for('users'))
				elif get_user.level == 3:
					# get_student
					get_student = student.get(student.id_user == id_user)
					if get_student.photo != 'default.png':
						# remove photo
						os.remove(os.path.join(app.config['folderimage'],get_student.photo))
					# delete student
					delete_student = student.delete().where(student.id_user == id_user)
					delete_student.execute()
					# delete related conseling
					del_conseling = conseling.delete().where(conseling.user_ask == id_user)
					del_conseling.execute()
					# delete user
					delete_user = user.delete().where(user.id == id_user)
					delete_user.execute()
					return redirect(url_for('users'))
				else:
					return redirect(url_for('users'))
			else:
				return redirect(url_for('users'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/profile')
def profile():
	if 'login' in session:
		if session['level'] == 1:
			return redirect(url_for('dashboard'))
		else:
			# cek if id_user is exists
			id_user = session['id_user']
			cek_user = user.select().where(user.id == id_user)
			if cek_user.exists():
				cek_user = cek_user.get()
				if cek_user.level == 2:
					get_profile = teacher.get(teacher.id_user == cek_user.id)
					return render_template('profile.html',data_user=cek_user, profile=get_profile)
				elif cek_user.level == 3:
					get_profile = student.get(student.id_user == cek_user.id)
					return render_template('profile.html',data_user=cek_user, profile=get_profile)
				else:
					return redirect(url_for('dashboard'))
			else:
					return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/edit-profile/<id_user>',methods=['POST'])
def edit_profile(id_user):
	if 'login' in session:
		if int(session['id_user']) == int(id_user):
			nama = request.form['nama']
			kelamin = request.form['jk']
			email = str(request.form['email']).lower()
			password = request.form['password']
			file = request.files['file']
			
			#cek user
			cek_user = user.select().where(user.id == id_user)
			if cek_user.exists():
				cek_user = cek_user.get()
				cek_email = user.select().where(user.email == email)
				if cek_user.level == 2:
					if cek_email.exists():
						cek_email = cek_email.get()
						if int(cek_email.id) == int(id_user):
							update_user = user.update(email=email,password=password).where(user.id == id_user)
							update_teacher = teacher.update(nama=nama,kelamin=kelamin).where(teacher.id_user == id_user)
							update_user.execute()
							update_teacher.execute()
							set_image = upload_image(file,cek_user.id,cek_user.level)
							session['photo'] = set_image
							return redirect(url_for('profile'))
						else:
							return redirect(url_for('profile'))
					else:
						update_user = user.update(email=email,password=password).where(user.id == id_user)
						update_teacher = teacher.update(nama=nama,kelamin=kelamin).where(teacher.id_user == id_user)
						update_user.execute()
						update_teacher.execute()
						set_image = upload_image(file,cek_user.id,cek_user.level)
						session['photo'] = set_image
						return redirect(url_for('profile'))
				elif cek_user.level == 3:
					if cek_email.exists():
						cek_email = cek_email.get()
						if int(cek_email.id) == int(id_user):
							update_user = user.update(email=email,password=password).where(user.id == id_user)
							update_student = student.update(nama=nama,kelamin=kelamin).where(student.id_user == id_user)
							update_user.execute()
							update_student.execute()
							set_image = upload_image(file,cek_user.id,cek_user.level)
							session['photo'] = set_image
							return redirect(url_for('profile'))
						else:
							return redirect(url_for('profile'))
					else:
						update_user = user.update(email=email,password=password).where(user.id == id_user)
						update_student = student.update(nama=nama,kelamin=kelamin).where(student.id_user == id_user)
						update_user.execute()
						update_student.execute()
						set_image = upload_image(file,cek_user.id,cek_user.level)
						session['photo'] = set_image
						return redirect(url_for('profile'))
				else:
					return redirect(url_for('dashboard'))
			else:
				return redirect(url_for('dashboard'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/conseling')
def conselings():
	if 'login' in session:
		if session['level'] == 1:
			data_conseling = conseling.select().order_by(conseling.dateask.desc())
			data_student = student.select()
			return render_template('conseling.html',conseling=data_conseling,data_student=data_student)
		elif session['level'] == 2:
			data_student = student.select()
			unanswered_question = conseling.select().where(conseling.answered == False)
			question_you_answer = conseling.select().where(conseling.user_answer == session['id_user'])
			return render_template('conseling.html',data_student=data_student ,unanswered_question=unanswered_question, question_you_answer=question_you_answer)
		else:
			data_student = student.select()
			your_question = conseling.select().where(conseling.user_ask == session['id_user'])
			return render_template('conseling.html',data_student=data_student,your_question=your_question)
	else:
		return redirect(url_for('login'))

@app.route('/create-conseling',methods=['POST'])
def create_conseling():
	if 'login' in session:
		if session['level'] == 3:
			if cek_user(session['id_user']) == False:
				return redirect(url_for('dashboard'))
			waktu = time.time()
			waktu_print = datetime.datetime.fromtimestamp(waktu).strftime('%Y-%m-%d %H:%M:%S')
			title = request.form['title']
			question = request.form['question']
			conseling.create(
				user_ask = session['id_user'],
				title = title,
				question = question,
				dateask = waktu,
				dateask_print = waktu_print
			)
			return redirect(url_for('conselings'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/conseling/<id_conseling>')
def detail_conseling(id_conseling):
	if 'login' in session:
		if session['level'] == 3:
			get_conseling = conseling.select().where(conseling.id == id_conseling)
			if get_conseling.exists():
				get_conseling = get_conseling.get()
				if int(str(get_conseling.user_ask)) == int(session['id_user']):
					data_student = student.get(student.id_user == get_conseling.user_ask)
					if get_conseling.answered == True:
						data_teacher = teacher.get(teacher.id_user == get_conseling.user_answer)
						return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student,data_teacher=data_teacher)
					else:
						return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student)
				else:
					return redirect(url_for('conselings'))
			else:
				return redirect(url_for('conselings'))
		elif session['level'] == 2:
			get_conseling = conseling.select().where(conseling.id == id_conseling)
			if get_conseling.exists():
				get_conseling = get_conseling.get()
				data_student = student.get(student.id_user == get_conseling.user_ask)
				if get_conseling.answered == True:
					if int(str(get_conseling.user_answer)) == session['id_user']:
						if get_conseling.answered == True:
							data_teacher = teacher.get(teacher.id_user == get_conseling.user_answer)
							return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student,data_teacher=data_teacher)
						else:
							return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student)
					else:
						return redirect(url_for('conselings'))
				else:
					return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student)
			else:
				return redirect(url_for('conselings'))
		else:
			get_conseling = conseling.select().where(conseling.id == id_conseling)
			if get_conseling.exists():
				get_conseling = get_conseling.get()
				data_student = student.get(student.id_user == get_conseling.user_ask)
				if get_conseling.answered == True:
					data_teacher = teacher.get(teacher.id_user == get_conseling.user_answer)
					return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student,data_teacher=data_teacher)
				else:
					return render_template('detail_conseling.html',data_conseling=get_conseling,data_student=data_student)
			else:
				return redirect(url_for('conselings'))
	else:
		return redirect(url_for('login'))

@app.route('/answer-conseling/<id_conseling>',methods=['POST'])
def answer_conseling(id_conseling):
	if 'login' in session:
		if session['level'] == 2:
			# get_conseling
			get_conseling = conseling.select().where(conseling.id == id_conseling)
			if get_conseling.exists():
				get_conseling = get_conseling.get()
				if get_conseling.answered == False:
					waktu = time.time()
					waktu_print = datetime.datetime.fromtimestamp(waktu).strftime('%Y-%m-%d %H:%M:%S')
					answer = request.form['answer']

					update_conseling = conseling.update(user_answer=session['id_user'],answer=answer,answered=True,dateans=waktu,dateans_print=waktu_print).where(conseling.id == id_conseling)
					update_conseling.execute()

					return redirect(url_for('detail_conseling',id_conseling=id_conseling))
				else:
					return redirect(url_for('conselings'))
			else:
				return redirect(url_for('conselings'))
		else:
			return redirect(url_for('conselings'))
	else:
		return redirect(url_for('login'))

@app.route('/edit-answer-conseling/<id_conseling>',methods=['POST'])
def edit_answer_conseling(id_conseling):
	if 'login' in session:
		if session['level'] == 2:
			get_conseling = conseling.select().where(conseling.id == id_conseling)
			if get_conseling.exists():
				get_conseling = get_conseling.get()
				if int(str(get_conseling.user_answer)) == int(session['id_user']):
					answer = request.form['answer']

					update_conseling=conseling.update(answer=answer).where(conseling.id == id_conseling)
					update_conseling.execute()
					return redirect(url_for('detail_conseling',id_conseling=id_conseling))
				else:
					return redirect(url_for('conselings'))
			else:
				return redirect(url_for('conselings'))
		else:
			return redirect(url_for('conselings'))
	else:
		return redirect(url_for('login'))

@app.route('/delete-conseling/<id_conseling>')
def delete_conseling(id_conseling):
	if 'login' in session:
		if session['level'] == 1:
			get_conseling = conseling.select().where(conseling.id == id_conseling)
			if get_conseling.exists():
				del_conseling = conseling.delete().where(conseling.id == id_conseling)
				del_conseling.execute()
				return redirect(url_for('conselings'))
			else:
				return redirect(url_for('conselings'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.route('/delete-all-conseling/')
def delete_all_conseling():
	if 'login' in session:
		if session['level'] == 1:
			del_conseling = conseling.delete()
			del_conseling.execute()
			return redirect(url_for('conselings'))
		else:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)
