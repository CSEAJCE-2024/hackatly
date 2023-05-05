from flask import Flask, render_template, request, url_for, session, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import *#form creation
from wtforms.validators import *
from flask_bcrypt import Bcrypt
from datetime import datetime, date
from sqlalchemy.sql import func
import random
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
    ratings = db.Column(db.Integer, nullable = False)
    
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
    itching = db.Column(db.Boolean, default=False, nullable=False)
    skin_rash = db.Column(db.Boolean, default=False, nullable=False)
    nodal_skin_eruptions = db.Column(db.Boolean, default=False, nullable=False)
    continuous_sneezing = db.Column(db.Boolean, default=False, nullable=False)
    shivering = db.Column(db.Boolean, default=False, nullable=False)
    chills = db.Column(db.Boolean, default=False, nullable=False)
    joint_pain = db.Column(db.Boolean, default=False, nullable=False)
    stomach_pain = db.Column(db.Boolean, default=False, nullable=False)
    acidity = db.Column(db.Boolean, default=False, nullable=False)
    ulcers_on_tongue = db.Column(db.Boolean, default=False, nullable=False)
    muscle_wasting = db.Column(db.Boolean, default=False, nullable=False)
    vomiting = db.Column(db.Boolean, default=False, nullable=False)
    burning_micturition = db.Column(db.Boolean, default=False, nullable=False)
    spotting_urination = db.Column(db.Boolean, default=False, nullable=False)
    fatigue = db.Column(db.Boolean, default=False, nullable=False)
    weight_gain = db.Column(db.Boolean, default=False, nullable=False)
    anxiety = db.Column(db.Boolean, default=False, nullable=False)
    cold_hands_and_feets = db.Column(db.Boolean, default=False, nullable=False)
    mood_swings = db.Column(db.Boolean, default=False, nullable=False)
    weight_loss = db.Column(db.Boolean, default=False, nullable=False)
    restlessness = db.Column(db.Boolean, default=False, nullable=False)
    lethargy = db.Column(db.Boolean, default=False, nullable=False)
    patches_in_throat = db.Column(db.Boolean, default=False, nullable=False)
    irregular_sugar_level = db.Column(db.Boolean, default=False, nullable=False)
    cough = db.Column(db.Boolean, default=False, nullable=False)
    high_fever = db.Column(db.Boolean, default=False, nullable=False)
    sunken_eyes = db.Column(db.Boolean, default=False, nullable=False)
    breathlessness = db.Column(db.Boolean, default=False, nullable=False)
    sweating = db.Column(db.Boolean, default=False, nullable=False)
    dehydration = db.Column(db.Boolean, default=False, nullable=False)
    indigestion = db.Column(db.Boolean, default=False, nullable=False)
    headache = db.Column(db.Boolean, default=False, nullable=False)
    yellowish_skin = db.Column(db.Boolean, default=False, nullable=False)
    dark_urine = db.Column(db.Boolean, default=False, nullable=False)
    nausea = db.Column(db.Boolean, default=False, nullable=False)
    loss_of_appetite = db.Column(db.Boolean, default=False, nullable=False)
    pain_behind_the_eyes = db.Column(db.Boolean, default=False, nullable=False)
    back_pain = db.Column(db.Boolean, default=False, nullable=False)
    constipation = db.Column(db.Boolean, default=False, nullable=False)
    abdominal_pain = db.Column(db.Boolean, default=False, nullable=False)
    diarrhoea = db.Column(db.Boolean, default=False, nullable=False)
    mild_fever = db.Column(db.Boolean, default=False, nullable=False)
    yellow_urine = db.Column(db.Boolean, default=False, nullable=False)
    yellowing_of_eyes = db.Column(db.Boolean, default=False, nullable=False)
    acute_liver_failure = db.Column(db.Boolean, default=False, nullable=False)
    fluid_overload = db.Column(db.Boolean, default=False, nullable=False)
    swelling_of_stomach = db.Column(db.Boolean, default=False, nullable=False)
    swelled_lymph_nodes = db.Column(db.Boolean, default=False, nullable=False)
    malaise = db.Column(db.Boolean, default=False, nullable=False)
    blurred_and_distorted_vision = db.Column(db.Boolean, default=False, nullable=False)
    phlegm = db.Column(db.Boolean, default=False, nullable=False)
    throat_irritation = db.Column(db.Boolean, default=False, nullable=False)
    redness_of_eyes = db.Column(db.Boolean, default=False, nullable=False)
    sinus_pressure = db.Column(db.Boolean, default=False, nullable=False)
    runny_nose = db.Column(db.Boolean, default=False, nullable=False)
    congestion = db.Column(db.Boolean, default=False, nullable=False)
    chest_pain = db.Column(db.Boolean, default=False, nullable=False)
    weakness_in_limbs = db.Column(db.Boolean, default=False, nullable=False)
    fast_heart_rate = db.Column(db.Boolean, default=False, nullable=False)
    pain_during_bowel_movements = db.Column(db.Boolean, default=False, nullable=False)
    pain_in_anal_region = db.Column(db.Boolean, default=False, nullable=False)
    bloody_stool = db.Column(db.Boolean, default=False, nullable=False)
    irritation_in_anus = db.Column(db.Boolean, default=False, nullable=False)
    neck_pain = db.Column(db.Boolean, default=False, nullable=False)
    dizziness = db.Column(db.Boolean, default=False, nullable=False)
    cramps = db.Column(db.Boolean, default=False, nullable=False)
    bruising = db.Column(db.Boolean, default=False, nullable=False)
    obesity = db.Column(db.Boolean, default=False, nullable=False)
    swollen_legs = db.Column(db.Boolean, default=False, nullable=False)
    swollen_blood_vessels = db.Column(db.Boolean, default=False, nullable=False)
    puffy_face_and_eyes = db.Column(db.Boolean, default=False, nullable=False)
    enlarged_thyroid = db.Column(db.Boolean, default=False, nullable=False)
    brittle_nails = db.Column(db.Boolean, default=False, nullable=False)
    swollen_extremeties = db.Column(db.Boolean, default=False, nullable=False)
    excessive_hunger = db.Column(db.Boolean, default=False, nullable=False)
    extra_marital_contacts = db.Column(db.Boolean, default=False, nullable=False)
    drying_and_tingling_lips = db.Column(db.Boolean, default=False, nullable=False)
    slurred_speech = db.Column(db.Boolean, default=False, nullable=False)
    knee_pain = db.Column(db.Boolean, default=False, nullable=False)
    hip_joint_pain = db.Column(db.Boolean, default=False, nullable=False)
    muscle_weakness = db.Column(db.Boolean, default=False, nullable=False)
    stiff_neck = db.Column(db.Boolean, default=False, nullable=False)
    swelling_joints = db.Column(db.Boolean, default=False, nullable=False)
    movement_stiffness = db.Column(db.Boolean, default=False, nullable=False)
    spinning_movements = db.Column(db.Boolean, default=False, nullable=False)
    loss_of_balance = db.Column(db.Boolean, default=False, nullable=False)
    unsteadiness = db.Column(db.Boolean, default=False, nullable=False)
    weakness_of_one_body_side = db.Column(db.Boolean, default=False, nullable=False)
    loss_of_smell = db.Column(db.Boolean, default=False, nullable=False)
    bladder_discomfort = db.Column(db.Boolean, default=False, nullable=False)
    foul_smell_of_urine = db.Column(db.Boolean, default=False, nullable=False)
    continuous_feel_of_urine = db.Column(db.Boolean, default=False, nullable=False)
    passage_of_gases = db.Column(db.Boolean, default=False, nullable=False)
    internal_itching = db.Column(db.Boolean, default=False, nullable=False)
    toxic_look = db.Column(db.Boolean, default=False, nullable=False)
    depression = db.Column(db.Boolean, default=False, nullable=False)
    irritability = db.Column(db.Boolean, default=False, nullable=False)
    muscle_pain = db.Column(db.Boolean, default=False, nullable=False)
    altered_sensorium = db.Column(db.Boolean, default=False, nullable=False)
    red_spots_over_body = db.Column(db.Boolean, default=False, nullable=False)
    belly_pain = db.Column(db.Boolean, default=False, nullable=False)
    abnormal_menstruation = db.Column(db.Boolean, default=False, nullable=False)
    dischromic_patches = db.Column(db.Boolean, default=False, nullable=False)
    watering_from_eyes = db.Column(db.Boolean, default=False, nullable=False)
    increased_appetite = db.Column(db.Boolean, default=False, nullable=False)
    polyuria = db.Column(db.Boolean, default=False, nullable=False)
    family_history = db.Column(db.Boolean, default=False, nullable=False)
    mucoid_sputum = db.Column(db.Boolean, default=False, nullable=False)
    rusty_sputum = db.Column(db.Boolean, default=False, nullable=False)
    lack_of_concentration = db.Column(db.Boolean, default=False, nullable=False)
    visual_disturbances = db.Column(db.Boolean, default=False, nullable=False)
    receiving_blood_transfusion = db.Column(db.Boolean, default=False, nullable=False)
    receiving_unsterile_injections = db.Column(db.Boolean, default=False, nullable=False)
    coma = db.Column(db.Boolean, default=False, nullable=False)
    stomach_bleeding = db.Column(db.Boolean, default=False, nullable=False)
    distention_of_abdomen = db.Column(db.Boolean, default=False, nullable=False)
    history_of_alcohol_consumption = db.Column(db.Boolean, default=False, nullable=False)
    fluid_overload = db.Column(db.Boolean, default=False, nullable=False)
    blood_in_sputum = db.Column(db.Boolean, default=False, nullable=False)
    prominent_veins_on_calf = db.Column(db.Boolean, default=False, nullable=False)
    palpitations = db.Column(db.Boolean, default=False, nullable=False)
    painful_walking = db.Column(db.Boolean, default=False, nullable=False)
    pus_filled_pimples = db.Column(db.Boolean, default=False, nullable=False)
    skin_peeling = db.Column(db.Boolean, default=False, nullable=False)
    silver_like_dusting = db.Column(db.Boolean, default=False, nullable=False)
    small_dents_in_nails = db.Column(db.Boolean, default=False, nullable=False)
    inflammatory_nails = db.Column(db.Boolean, default=False, nullable=False)
    blister = db.Column(db.Boolean, default=False, nullable=False)
    red_sore_around_nose = db.Column(db.Boolean, default=False, nullable=False)
    red_sore_around_nose = db.Column(db.Boolean, default=False, nullable=False)


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
    docName = SelectField("Select Doctor", choices=[('doctor1', 'Dr. John Blake'), ('doctor2', 'Dr. Ram Kumar')])
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
        form = MedicalHistoryForm(obj=patient)
        return render_template('viewpatient.html', patient = patient, form=form)
    else:
        return redirect(url_for('home'))



# APPOINTMENT
@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():

    image_urls =[
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvp4fRP0z_n7aGQlOPqy4odkguvV5-gz5E6fMnoa4F7NU1J8Y7T3gxzPxGjzg9gZDgSms&usqp=CAU",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTCUaHd-IXCbYDJMTQGeikLyQuzDMX-zSz8iAQ4fxJyhfv-3czWAeqt9q0WvI7CnGYCYWw&usqp=CAU",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSXQicZ3Hqf1JPXm9hR3IOv74H590fsZUBsHQ&usqp=CAU",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLrN0yIhXzu8SokLj7H7DSANmXPFZmQ-5A_Q8_Isr2WoKf3WAfheodxbbJWOmPXA8Vikk&usqp=CAU",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvV20C8_tKXoenQdXQmQUI3vUXr8Z9KoXW0wPcalm4BMKLPEGVpaFvjf2fDYIiT5njx4s&usqp=CAU",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS825lZxPEE8OxWxZo-1r6cJA5Ybbi2w-tH4K4cn6NrkCQksuPuSkTTNX30AMwfPwrEfAc&usqp=CAU"

    ]
    ratings = Hospital.query.order_by(Hospital.ratings.desc()).all()
    random.shuffle(image_urls)
    return render_template("appointment.html", image_urls = image_urls, ratings = ratings)

@app.route("/appointment/bookappointment/<int:id>", methods=["GET", "POST"])
@login_required
def bookappointment(id):
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
    slots = Appointment.query.group_by(Appointment.slot).order_by(func.count().desc()).all()
    max_booked_slot = slots[0].slot if slots else None

    return render_template("bookappointment.html", hosp_id = id, form=form, hospitals=hospitals, max_booked_slot=max_booked_slot)

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
        return render_template('preconsult.html', symptoms=symptoms)

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