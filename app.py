from flask import Flask, render_template, request, url_for, session, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import *#form creation
from wtforms.validators import *
from flask_bcrypt import Bcrypt
from datetime import datetime, date
from predictor.infer import predict_disease

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] ='secretkey'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "userlogin"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# CUSTOM FUNCTIONS
today = date.today()

def calculate_age(born):
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    if age <= 0:
        return 1
    else:
        return age
app.jinja_env.filters['calculate_age'] = calculate_age

def order_by_slot(appointment):
    return {'morning': 1, 'afternoon': 2, 'evening': 3}[appointment.slot]

# PORGRAM MODELS
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(80))
    city = db.Column(db.String(30))
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    is_doctor = db.Column(db.Boolean, default=False, nullable=False)
    mobile = db.Column(db.Integer)
    medical_conditions = db.Column(db.String(100), default="", nullable=False)
    allergies = db.Column(db.String(100), default="", nullable=False)
    medications = db.Column(db.String(100), default="", nullable=False)
    vaccine_history = db.Column(db.String(100), default="", nullable=False)
    family_history = db.Column(db.String(100), default="", nullable=False)
    surgical_history = db.Column(db.String(100), default="", nullable=False)
    lifestyle_habits = db.Column(db.String(100), default="", nullable=False)
    isFastrack = db.Column(db.Integer, default = 0, nullable = True)
    insurance = db.Column(db.String(20), nullable=False)
        
class Doctor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

class Location(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    mobile = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(10), nullable=False)
    accepted_insurance = db.Column(db.String(20), nullable=False)
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)

class Drivers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tel_id = db.Column(db.Integer, nullable = False)
    name = db.Column(db.String, nullable = False)

class VideoCall(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    video_id = db.Column(db.String, nullable = False)

class Symptoms(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    symptoms = db.Column(db.String, nullable = True)
    predicted_disease = db.Column(db.String, nullable = True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)

# ****** FORMS *******

class Doc_RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "User Name"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Full Name"})
    gender = RadioField('Gender', choices=[('Male'),('Female'),('Other')])
    dob = DateField(validators=[InputRequired()],render_kw={"placeholder": "Date of Birth"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("Username already exists.")

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "User Name"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Full Name"})
    gender = RadioField('Gender', choices=[('Male'),('Female')])
    address = StringField(validators=[InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Address"})
    mobile = StringField(validators=[InputRequired(), Length(min=10, max=12)], render_kw={"placeholder": "Mobile No."})
    city = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "City"})
    dob = DateField(validators=[InputRequired()],render_kw={"placeholder": "Date of Birth"})
    submit = SubmitField("Register")

    # confirm = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Confirm Password"})
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("Username already exists.")
    
class EditForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "User Name"}, name='username')
    name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Full Name"}, name='name')
    gender = RadioField('Gender', choices=[('Male'),('Female'),('Other')], name='gender')
    address = StringField(validators=[InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Address"}, name='address')
    mobile = StringField(validators=[InputRequired(), Length(min=10, max=12)], render_kw={"placeholder": "Mobile No."}, name='mobile')
    city = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "City"}, name='city')
    dob = DateField(validators=[InputRequired()],render_kw={"placeholder": "Date of Birth"}, name='dob')
    submit = SubmitField("Save Changes")



class AppointmentForm(FlaskForm):
    slot = SelectField("Appointment Slot", choices=[("morning", "Morning (9am-12pm)"), ("afternoon", "Afternoon (1pm-4pm) Peak time"), ("evening", "Evening (5pm-8pm)")], validators=[InputRequired()])
    docDept = SelectField("Select Doctor Department", choices=[("practitioner","General Practitioner"),("cardiologist", "Cardiologist"), ("pediatrician", "Pediatrician"), ("dermatologist","Dermatologist"), ("dentist", "Dentist")])
    date = DateField("Appointment Date",validators=[InputRequired()])
    submit = SubmitField("Book Appointment",validators=[InputRequired()])

class MedicalHistoryForm(FlaskForm):
    medical_conditions = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Medical Conditions"}, name='medical_conditions')
    allergies = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Allergies"}, name='allergies')
    medications = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Medications"}, name='medications')
    vaccine_history = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Vaccine History"}, name='vaccine_history')
    family_history = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Family History"}, name='family_history')
    surgical_history = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Surgical History"}, name='surgical_history')
    lifestyle_habits = StringField(validators=[Length(max=200)], render_kw={"placeholder": "Lifestyle Habits"}, name='lifestyle_habits')
    submit = SubmitField("Submit",validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Login")

# ******** ROUTES ********
# REGISTRATION
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        insurance = request.form["insurance"]
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, name=form.name.data, address = form.address.data, city = form.city.data, dob=form.dob.data,gender=form.gender.data, is_doctor = False, mobile = form.mobile.data, insurance=insurance)
        db.session.add(new_user)
        db.session.commit()
        flash("You have successfully registered! Please login to continue.")
        return redirect(url_for('userlogin'))
    
    insurances = Hospital.query.with_entities(Hospital.accepted_insurance).distinct().all()
    return render_template("register.html", form=form, insurances=insurances)

@app.route("/doctorRegister", methods=['GET','POST'])
def doctorRegister():
    form = Doc_RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, name=form.name.data, dob=form.dob.data, gender=form.gender.data, is_doctor = True, insurance = "Doctor Insurance")
        db.session.add(new_user)
        db.session.commit()
        flash("You have successfully registered! Please login to continue.")
        return redirect(url_for('doctorlogin'))
    
    return render_template("doctorRegister.html", form=form)

@app.route("/")
def index():
    appointments = Appointment.query.order_by(Appointment.date).all()
    return render_template("index.html", appointments=appointments)


# LOGIN
@app.route("/userlogin", methods=['GET','POST'])
def userlogin():
    form = LoginForm()    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return(redirect(url_for('home')))
        else:
            flash("Invalid username or password")
            return redirect(url_for('userlogin'))
    return render_template("userlogin.html", form=form)
    

@app.route("/doctorlogin", methods=['GET','POST'])
def doctorlogin():
    form = LoginForm()    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return(redirect(url_for('home')))
        else:
            flash("Invalid username or password")
            return redirect(url_for('doctorlogin'))
    return render_template("doctorlogin.html", form=form)


# DASHBOARD
@app.route("/home", methods = ['GET', 'POST'])
@login_required
def home():
    check_user = User.query.filter_by(id = current_user.id).first()
    if check_user.is_doctor:
        past_appointments = Appointment.query.filter(Appointment.date < today).all()
        for appointment in past_appointments:
            db.session.delete(appointment)
        db.session.commit()

        appointments = db.session.query(Appointment, User).join(User).filter(Appointment.date == date.today()).order_by(db.case({
            'morning': 1,
            'afternoon': 2,
            'evening': 3
        }, value=Appointment.slot)).all()
        notdone_appointments = Appointment.query.filter_by(status=False).count()
        done_appointments = Appointment.query.filter_by(status=True).count()

    else:
        appointments = None
        done_appointments = None
        notdone_appointments = None
    return render_template("home.html", appointments = appointments, notdone_appointments = notdone_appointments, done_appointments = done_appointments)



@app.route("/myappointments/<int:id>", methods=['GET','POST'])
@app.route("/myappointments/")
@login_required
def myappointments(id=None):
    check_user = User.query.filter_by(id = current_user.id).first()
    if check_user.is_doctor:
        appointments = db.session.query(Appointment, User).join(User).filter(Appointment.date == date.today()).filter(Appointment.status == False).order_by(db.case({
            'morning': 1,
            'afternoon': 2,
            'evening': 3
        }, value=Appointment.slot)).all()
    else:
        appointments = Appointment.query.filter_by(user_id = current_user.id).all()

    appointment = None
    if id is not None:
        appointment = db.session.query(Appointment, User).join(User).filter(Appointment.id == id).all()
    hospital = db.session.query(Appointment, Hospital).join(Hospital).all()
    return render_template("myappointments.html", appointments=appointments, appointment=appointment, id=id, hospitals=hospital)

# PROFILE
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = MedicalHistoryForm(obj=current_user)
    return render_template("profile.html", form=form)


@app.route("/medical_history", methods=['POST'])
@login_required
def medical_history():
    """ medical_conditions = request.form.medical_conditions
    allergies = request.form.allergies
    medications = request.form.medications
    vaccine_history = request.form.vaccine_history
    family_history = request.form.family_history
    surgical_history = request.form.surgical_history
    lifestyle_habits = request.form.lifestyle_habits """
    form = MedicalHistoryForm()
    form.populate_obj(current_user)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', form=form)

@app.route("/delete_profile", methods=['GET', 'POST'])
@login_required
def delete_profile():
    user_id = current_user.id
    User.query.filter_by(id=user_id).delete()
    Appointment.query.filter_by(user_id = user_id).delete()
    db.session.commit()
    return redirect(url_for('logout'))

# PATIENTS
@app.route("/mypatients", methods=['GET', 'POST'])
@login_required
def mypatients():
    if current_user.is_doctor:
        patients = User.query.filter_by(is_doctor = False).all()
        return render_template('mypatients.html', patients = patients)
    else:
        return redirect(url_for('home'))

@app.route("/viewpatient/<int:id>", methods=['GET', 'POST'])
@login_required
def viewpatient(id):
    if current_user.is_doctor:
        patient = User.query.filter_by(id = id).first()
        return render_template('viewpatient.html', patient = patient)
    else:
        return redirect(url_for('home'))



# APPOINTMENT
@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        hospital_id = request.form['hospital_id']
        slot = form.slot.data
        date = form.date.data
        appointment = Appointment(user_id = current_user.id, slot=slot, date=date, status=False, hospital_id=hospital_id)
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for("myappointments"))
    hospitals = Hospital.query.all()
    return render_template("appointment.html", form=form, hospitals=hospitals)



@app.route('/delete_appointment/<int:id>', methods=['POST','GET'])
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get(id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('myappointments'))

@app.route('/preconsult/<int:id>', methods=['POST','GET'])
@login_required
def preconsult(id):
    if request.method == "GET":
        symptoms = ['itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering', 'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_ urination', 'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat', 'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration', 'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs', 'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine', 'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)', 'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation', 'dischromic _patches', 'watering_from_eyes', 'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption', 'fluid_overload.1', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples','skin_peeling','silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose','red_sore_around_nose']
        return render_template('preconsult.html', symptoms=symptoms, id=id)
    else:
        symptoms = {'itching': 0, 'skin_rash': 0, 'nodal_skin_eruptions': 0, 'continuous_sneezing': 0,
                'shivering': 0, 'chills': 0, 'joint_pain': 0, 'stomach_pain': 0, 'acidity': 0, 'ulcers_on_tongue': 0,
                'muscle_wasting': 0, 'vomiting': 0, 'burning_micturition': 0, 'spotting_ urination': 0, 'fatigue': 0,
                'weight_gain': 0, 'anxiety': 0, 'cold_hands_and_feets': 0, 'mood_swings': 0, 'weight_loss': 0,
                'restlessness': 0, 'lethargy': 0, 'patches_in_throat': 0, 'irregular_sugar_level': 0, 'cough': 0,
                'high_fever': 0, 'sunken_eyes': 0, 'breathlessness': 0, 'sweating': 0, 'dehydration': 0,
                'indigestion': 0, 'headache': 0, 'yellowish_skin': 0, 'dark_urine': 0, 'nausea': 0, 'loss_of_appetite': 0,
                'pain_behind_the_eyes': 0, 'back_pain': 0, 'constipation': 0, 'abdominal_pain': 0, 'diarrhoea': 0, 'mild_fever': 0,
                'yellow_urine': 0, 'yellowing_of_eyes': 0, 'acute_liver_failure': 0, 'fluid_overload': 0, 'swelling_of_stomach': 0,
                'swelled_lymph_nodes': 0, 'malaise': 0, 'blurred_and_distorted_vision': 0, 'phlegm': 0, 'throat_irritation': 0,
                'redness_of_eyes': 0, 'sinus_pressure': 0, 'runny_nose': 0, 'congestion': 0, 'chest_pain': 0, 'weakness_in_limbs': 0,
                'fast_heart_rate': 0, 'pain_during_bowel_movements': 0, 'pain_in_anal_region': 0, 'bloody_stool': 0,
                'irritation_in_anus': 0, 'neck_pain': 0, 'dizziness': 0, 'cramps': 0, 'bruising': 0, 'obesity': 0, 'swollen_legs': 0,
                'swollen_blood_vessels': 0, 'puffy_face_and_eyes': 0, 'enlarged_thyroid': 0, 'brittle_nails': 0, 'swollen_extremeties': 0,
                'excessive_hunger': 0, 'extra_marital_contacts': 0, 'drying_and_tingling_lips': 0, 'slurred_speech': 0,
                'knee_pain': 0, 'hip_joint_pain': 0, 'muscle_weakness': 0, 'stiff_neck': 0, 'swelling_joints': 0, 'movement_stiffness': 0,
                'spinning_movements': 0, 'loss_of_balance': 0, 'unsteadiness': 0, 'weakness_of_one_body_side': 0, 'loss_of_smell': 0,
                'bladder_discomfort': 0, 'foul_smell_of urine': 0, 'continuous_feel_of_urine': 0, 'passage_of_gases': 0, 'internal_itching': 0,
                'toxic_look_(typhos)': 0, 'depression': 0, 'irritability': 0, 'muscle_pain': 0, 'altered_sensorium': 0,
                'red_spots_over_body': 0, 'belly_pain': 0, 'abnormal_menstruation': 0, 'dischromic _patches': 0, 'watering_from_eyes': 0,
                'increased_appetite': 0, 'polyuria': 0, 'family_history': 0, 'mucoid_sputum': 0, 'rusty_sputum': 0, 'lack_of_concentration': 0,
                'visual_disturbances': 0, 'receiving_blood_transfusion': 0, 'receiving_unsterile_injections': 0, 'coma': 0,
                'stomach_bleeding': 0, 'distention_of_abdomen': 0, 'history_of_alcohol_consumption': 0, 'fluid_overload.0': 0,
                'blood_in_sputum': 0, 'prominent_veins_on_calf': 0, 'palpitations': 0, 'painful_walking': 0, 'pus_filled_pimples': 0,
                'blackheads': 0, 'scurring': 0, 'skin_peeling': 0, 'silver_like_dusting': 0, 'small_dents_in_nails': 0, 'inflammatory_nails': 0,
                'blister': 0, 'red_sore_around_nose': 0, 'yellow_crust_ooze': 0}
        selected_symptoms = request.form.getlist('selected_symptom')
        for i in selected_symptoms:
            symptoms[i] = 1
        result = predict_disease(symptoms)
        insert_symptom = Symptoms(symptoms=','.join(selected_symptoms), predicted_disease=result, appointment_id=id)
        db.session.add(insert_symptom)
        db.session.commit()
        return redirect(url_for('myappointments'))

@app.route('/markDone/<int:id>', methods=['GET', 'POST'])
@login_required
def markDone(id):
    appointment = Appointment.query.get(id)
    appointment.status = True
    db.session.commit()
    return redirect(url_for('myappointments'))


# LOGOUT
@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('userlogin'))


@app.context_processor  
def inject_datetime():
    return dict(datetime=datetime)


@app.route("/updateFastTrack")
@login_required
def updateFastTrack():
    user = User.query.get(current_user.id)
    user.isFastrack = 1
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/save', methods = ['POST'])
def save():
    try:
        request_json = request.get_json()
        lat = request_json['lat']
        long = request_json['long']
        new_location = Location(latitude=lat, longitude=long)
        db.session.add(new_location)
        db.session.commit()
        return jsonify({
            "lat": lat,
            "long": long
        })
    except Exception as e:
        return e
    
@app.route('/registerDriver', methods = ['POST'])
def registerDriver():
    try:
        request_json = request.get_json()
        name = request_json['name']
        tel_id = request_json['tel_id']
        new_driver = Drivers(name=name, tel_id=tel_id)
        db.session.add(new_driver)
        db.session.commit()
        return jsonify({
            "status": "Successfully registered the driver!"
        })
    except Exception as e:
        return e

@app.route('/getHospital', methods = ['GET'])
def getHospital():
    hospitals = Hospital.query.all()
    hospital_list = []
    for hospital in hospitals:
        hosp_dict = {
            'name': hospital.name,
            'mobile': hospital.mobile
        }
        hospital_list.append(hosp_dict)
    return jsonify(hospital_list)

@app.route("/getDriver", methods = ['GET'])
def getDriver():
    driver = Drivers.query.all()
    driver_list = []
    for driver in driver:
        driver_dict = {
            'id': driver.id,
            'tel_id': driver.tel_id,
            'name': driver.name,
        }
        driver_list.append(driver_dict)
    print(jsonify(driver_list))
    return jsonify(driver_list)

@app.route("/videostart", methods = ['POST'])
def videostart():
    request_json = request.get_json()
    video_id = request_json['video_id']
    vc = VideoCall(video_id=video_id)
    db.session.add(vc)
    db.session.commit()
    return jsonify({
        'status': 200
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)