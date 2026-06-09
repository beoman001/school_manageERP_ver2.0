"""
School ERP System - Ultimate Backend Application
Features: Admissions, Fees, Exams, Chat, Video Uploads, Live Classes, Biodata.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# CONFIGURATION & SETUP
# ==========================================

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///school.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "schoolerp_super_secret_key_2026")

app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'mp4', 'webm', 'avi'}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_commit():
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        return False


# ==========================================
# DATABASE MODELS
# ==========================================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    roll_no = db.Column(db.String(20), unique=True)
    student_class = db.Column(db.String(20))
    division = db.Column(db.String(10))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    dob = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    address = db.Column(db.Text)
    profile_pic = db.Column(db.String(200), default="default.png")


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    teacher_id = db.Column(db.String(50), unique=True)
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    dob = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    address = db.Column(db.Text)
    qualification = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200), default="default.png")


class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_roll_no = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))


class Principal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))


# Original Features
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50))
    student_name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    division = db.Column(db.String(10))
    date = db.Column(db.String(50))
    status = db.Column(db.String(20))


class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50))
    student_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    exam_name = db.Column(db.String(100))
    marks = db.Column(db.Integer)


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50))
    student_name = db.Column(db.String(100))
    student_class = db.Column(db.String(50))
    total_fee = db.Column(db.Integer)
    paid_fee = db.Column(db.Integer)
    balance_fee = db.Column(db.Integer)
    status = db.Column(db.String(20))


class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_class = db.Column(db.String(50))
    day = db.Column(db.String(50))
    period1 = db.Column(db.String(100))
    period2 = db.Column(db.String(100))
    period3 = db.Column(db.String(100))
    period4 = db.Column(db.String(100))
    period5 = db.Column(db.String(100))
    period6 = db.Column(db.String(100))
    period7 = db.Column(db.String(100))
    period8 = db.Column(db.String(100))


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    due_date = db.Column(db.String(50))


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    assignment_title = db.Column(db.String(200))
    filename = db.Column(db.String(300))


class BusFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    route_name = db.Column(db.String(100))
    distance = db.Column(db.Float)
    fee = db.Column(db.Float)


class BusFeeSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fee_5km = db.Column(db.Float, default=500)
    fee_10km = db.Column(db.Float, default=1000)
    fee_15km = db.Column(db.Float, default=1500)
    fee_20km = db.Column(db.Float, default=2000)
    fee_above20km = db.Column(db.Float, default=2500)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    sender = db.Column(db.String(100))


class CertificateRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    roll_no = db.Column(db.String(50))
    request_type = db.Column(db.String(50))
    status = db.Column(db.String(50))


# Advanced Features
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    title = db.Column(db.String(200))
    student_class = db.Column(db.String(20))
    division = db.Column(db.String(10))
    filename = db.Column(db.String(300))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)


class VideoClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    title = db.Column(db.String(200))
    student_class = db.Column(db.String(20))
    division = db.Column(db.String(10))
    filename = db.Column(db.String(300))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)


class LiveClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    title = db.Column(db.String(200))
    student_class = db.Column(db.String(20))
    division = db.Column(db.String(10))
    meeting_link = db.Column(db.String(500))
    schedule_time = db.Column(db.String(100))


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(100))
    receiver_email = db.Column(db.String(100))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ClassFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_class = db.Column(db.String(50), unique=True)
    base_fee = db.Column(db.Integer)

# ==========================================
# DATABASE INITIALIZATION
# ==========================================

with app.app_context():
    db.drop_all()
    db.create_all()

    if not BusFeeSettings.query.first():
        db.session.add(BusFeeSettings(fee_5km=500, fee_10km=1000, fee_15km=1500, fee_20km=2000, fee_above20km=2500))

    if not Admin.query.filter_by(email="admin@gmail.com").first():
        db.session.add(Admin(name="Admin", email="admin@gmail.com", password=generate_password_hash("admin123")))

    if not Principal.query.filter_by(email="principal@gmail.com").first():
        db.session.add(
            Principal(name="Principal", email="principal@gmail.com", password=generate_password_hash("principal123")))
        # --- TEMPORARY TEST DATA (DELETE LATER) ---
        if not Teacher.query.filter_by(email="teacher@school.com").first():
            db.session.add(Teacher(
                name="Test Teacher",
                teacher_id="T001",
                subject="Science",
                email="teacher@school.com",
                password=generate_password_hash("password123")
            ))

        if not Student.query.filter_by(email="student@school.com").first():
            db.session.add(Student(
                name="Test Student",
                roll_no="101A",
                student_class="10",
                division="A",
                email="student@school.com",
                password=generate_password_hash("password123")
            ))
            if not Parent.query.filter_by(email="parent@school.com").first():
                db.session.add(Parent(
                    name="Test Parent",
                    student_roll_no="101A",  # Notice how this perfectly matches our test student!
                    phone="555-0199",
                    email="parent@school.com",
                    password=generate_password_hash("password123")
                ))
        # ------------------------------------------
    safe_commit()


# ==========================================
# AUTHENTICATION
# ==========================================

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    role = request.form.get("role")
    username = request.form.get("username")
    password = request.form.get("password")

    user = None
    if role == "Admin":
        user = Admin.query.filter_by(email=username).first()
    elif role == "Teacher":
        user = Teacher.query.filter_by(email=username).first()
    elif role == "Student":
        user = Student.query.filter_by(email=username).first()
    elif role == "Parent":
        user = Parent.query.filter_by(email=username).first()
    elif role == "Principal":
        user = Principal.query.filter_by(email=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_role'] = role
        session['user_email'] = user.email
        session['user_name'] = user.name
        return redirect(f"/{role.lower()}")

    flash("Invalid Credentials")
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ==========================================
# DASHBOARDS & RENDERING ROUTES
# ==========================================

@app.route("/admin")
def admin(): return render_template("admin_dashboard.html", student_count=Student.query.count(),
                                    teacher_count=Teacher.query.count(), parent_count=Parent.query.count())


@app.route("/teacher")
def teacher(): return render_template("teacher_dashboard.html")


@app.route("/student")
def student(): return render_template("student_dashboard.html")


@app.route("/parent")
def parent(): return render_template("parent_dashboard.html")


@app.route("/principal")
def principal(): return render_template("principal_dashboard.html")


# Render standard templates
@app.route("/add-student")
def add_student(): return render_template("add_student.html")


@app.route("/add-teacher")
def add_teacher(): return render_template("add_teacher.html")


@app.route("/add-parent")
def add_parent(): return render_template("add_parent.html")


@app.route("/fee-management")
def fee_management(): return render_template("fee_management.html")


@app.route("/bus-fee-management")
def bus_fee_management(): return render_template("bus_fee_management.html")


@app.route("/exam-management")
def exam_management(): return render_template("exam_management.html")


@app.route("/timetable-management")
def timetable_management(): return render_template("timetable_management.html")


@app.route("/mark-attendance")
def mark_attendance(): return render_template("mark_attendance.html")


@app.route("/enter-marks")
def enter_marks(): return render_template("enter_marks.html")


@app.route("/upload-notes")
def upload_notes(): return render_template("upload_notes.html")


@app.route("/create-assignment")
def create_assignment(): return render_template("create_assignment.html")


@app.route("/view-attendance")
def view_attendance():
    # If a student clicks it, show them their custom visual calendar
    if session.get('user_role') == 'Student':
        student = Student.query.get(session['user_id'])
        records = Attendance.query.filter_by(roll_no=student.roll_no).all()
        return render_template("attendance_calendar.html", records=records)

    # If a teacher or admin clicks it, take them to the master logs
    return redirect("/attendance-report")


@app.route("/exam-schedule")
def exam_schedule(): return render_template("exam_schedule.html")


@app.route("/request-tc")
def request_tc(): return render_template("request_tc.html")


@app.route("/request-migration")
def request_migration(): return render_template("request_migration.html")


@app.route("/submit-assignment")
def submit_assignment(): return render_template("submit_assignment.html")


@app.route("/create-announcement")
def create_announcement(): return render_template("create_announcement.html")


@app.route("/chat")
def chat(): return render_template("chat.html")


# ==========================================
# CRUD OPERATIONS (YOUR ORIGINAL ROUTES)
# ==========================================

# Students
@app.route("/manage-students")
def manage_students(): return render_template("manage_students.html", students=Student.query.all())


@app.route("/save-student", methods=["POST"])
def save_student():
    student = Student(
        name=request.form.get("name"),
        roll_no=request.form.get("roll_no"),
        student_class=request.form.get("student_class"),
        division=request.form.get("division"),
        parent_name=request.form.get("parent_name"),
        parent_phone=request.form.get("parent_phone"),
        email=request.form.get("email"),
        password=generate_password_hash(request.form.get("password"))
    )
    db.session.add(student)
    safe_commit()
    return redirect("/manage-students")


@app.route("/edit-student/<int:id>")
def edit_student(id): return render_template("edit_student.html", student=Student.query.get_or_404(id))


@app.route("/update-student/<int:id>", methods=["POST"])
def update_student(id):
    student = Student.query.get_or_404(id)
    student.name = request.form.get("name")
    student.roll_no = request.form.get("roll_no")
    student.student_class = request.form.get("student_class")
    safe_commit()
    return redirect("/manage-students")


@app.route("/delete-student/<int:id>")
def delete_student(id):
    db.session.delete(Student.query.get_or_404(id))
    safe_commit()
    return redirect("/manage-students")


# Teachers
@app.route("/manage-teachers")
def manage_teachers(): return render_template("manage_teachers.html", teachers=Teacher.query.all())


@app.route("/save-teacher", methods=["POST"])
def save_teacher():
    teacher = Teacher(
        name=request.form.get("name"),
        teacher_id=request.form.get("teacher_id"),
        subject=request.form.get("subject"),
        phone=request.form.get("phone"),
        email=request.form.get("email"),
        password=generate_password_hash(request.form.get("password"))
    )
    db.session.add(teacher)
    safe_commit()
    return redirect("/manage-teachers")


@app.route("/edit-teacher/<int:id>")
def edit_teacher(id): return render_template("edit_teacher.html", teacher=Teacher.query.get_or_404(id))


@app.route("/update-teacher/<int:id>", methods=["POST"])
def update_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    teacher.name = request.form.get("name")
    teacher.teacher_id = request.form.get("teacher_id")
    teacher.subject = request.form.get("subject")
    safe_commit()
    return redirect("/manage-teachers")


@app.route("/delete-teacher/<int:id>")
def delete_teacher(id):
    db.session.delete(Teacher.query.get_or_404(id))
    safe_commit()
    return redirect("/manage-teachers")


# Parents
@app.route("/manage-parents")
def manage_parents(): return render_template("manage_parents.html", parents=Parent.query.all())


@app.route("/save-parent", methods=["POST"])
def save_parent():
    parent = Parent(
        name=request.form.get("name"),
        student_roll_no=request.form.get("student_roll_no"),
        phone=request.form.get("phone"),
        email=request.form.get("email"),
        password=generate_password_hash(request.form.get("password"))
    )
    db.session.add(parent)
    safe_commit()
    return redirect("/manage-parents")


@app.route("/delete-parent/<int:id>")
def delete_parent(id):
    db.session.delete(Parent.query.get_or_404(id))
    safe_commit()
    return redirect("/manage-parents")


# ==========================================
# FEES & BUS FEES (YOUR ORIGINAL ROUTES)
# ==========================================

@app.route("/save-fee", methods=["POST"])
def save_fee():
    total_fee = int(request.form.get("total_fee", 0))
    paid_fee = int(request.form.get("paid_fee", 0))
    fee = Fee(
        roll_no=request.form.get("roll_no"),
        student_name=request.form.get("student_name"),
        student_class=request.form.get("student_class"),
        total_fee=total_fee,
        paid_fee=paid_fee,
        balance_fee=total_fee - paid_fee,
        status="Paid" if (total_fee - paid_fee) == 0 else "Pending"
    )
    db.session.add(fee)
    safe_commit()
    return redirect("/fee-report")


@app.route("/fee-report")
@app.route("/view-fees")
def fee_report(): return render_template("fee_report.html", fees=Fee.query.all())


@app.route("/bus-fee-settings")
def bus_fee_settings(): return render_template("bus_fee_settings.html", settings=BusFeeSettings.query.first())


@app.route("/update-bus-fee-settings", methods=["POST"])
def update_bus_fee_settings():
    settings = BusFeeSettings.query.first()
    settings.fee_5km = float(request.form.get("fee_5km"))
    settings.fee_10km = float(request.form.get("fee_10km"))
    settings.fee_15km = float(request.form.get("fee_15km"))
    settings.fee_20km = float(request.form.get("fee_20km"))
    settings.fee_above20km = float(request.form.get("fee_above20km"))
    safe_commit()
    return redirect("/bus-fee-settings")


@app.route("/save-bus-fee", methods=["POST"])
def save_bus_fee():
    distance = float(request.form.get("distance", 0))
    settings = BusFeeSettings.query.first()

    if distance <= 5:
        fee_amt = settings.fee_5km
    elif distance <= 10:
        fee_amt = settings.fee_10km
    elif distance <= 15:
        fee_amt = settings.fee_15km
    elif distance <= 20:
        fee_amt = settings.fee_20km
    else:
        fee_amt = settings.fee_above20km

    db.session.add(BusFee(student_name=request.form.get("student_name"), route_name=request.form.get("route_name"),
                          distance=distance, fee=fee_amt))
    safe_commit()
    return redirect("/bus-fee-report")


@app.route("/bus-fee-report")
@app.route("/view-bus-fees")
@app.route("/view-bus-fee")
def bus_fee_report(): return render_template("bus_fee_report.html", fees=BusFee.query.all())


# ==========================================
# ACADEMICS & COMMUNICATIONS (YOUR ORIGINAL ROUTES)
# ==========================================

@app.route("/save-attendance", methods=["POST"])
def save_attendance():
    db.session.add(Attendance(roll_no=request.form.get("roll_no"), student_name=request.form.get("student_name"),
                              date=request.form.get("date"), status=request.form.get("status")))
    safe_commit()
    return redirect("/attendance-report")


@app.route("/attendance-report")
def attendance_report(): return render_template("attendance_report.html", records=Attendance.query.all())


@app.route("/save-marks", methods=["POST"])
def save_marks():
    db.session.add(Marks(roll_no=request.form.get("roll_no"), student_name=request.form.get("student_name"),
                         subject=request.form.get("subject"), exam_name=request.form.get("exam_name"),
                         marks=request.form.get("marks")))
    safe_commit()
    return redirect("/marks-report")


@app.route("/marks-report")
def marks_report(): return render_template("marks_report.html", marks=Marks.query.all())


@app.route("/view-marks")
def view_marks(): return render_template("view_marks.html", marks=Marks.query.all())


@app.route("/save-notes", methods=["POST"])
def save_notes():
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            db.session.add(
                Notes(subject=request.form.get("subject"), title=request.form.get("title"), filename=filename))
            safe_commit()
    return redirect("/notes-library")


@app.route("/notes-library")
@app.route("/download-notes")
def notes_library(): return render_template("notes_library.html", notes=Notes.query.all())


@app.route("/save-assignment", methods=["POST"])
def save_assignment():
    db.session.add(Assignment(title=request.form.get("title"), subject=request.form.get("subject"),
                              due_date=request.form.get("due_date")))
    safe_commit()
    return redirect("/assignment-list")


@app.route("/assignment-list")
def assignment_list(): return render_template("assignment_list.html", assignments=Assignment.query.all())


@app.route("/save-submission", methods=["POST"])
def save_submission():
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            db.session.add(Submission(student_name=request.form.get("student_name"),
                                      assignment_title=request.form.get("assignment_title"), filename=filename))
            safe_commit()
    return redirect("/view-submissions")


@app.route("/view-submissions")
def view_submissions(): return render_template("view_submissions.html", submissions=Submission.query.all())


@app.route("/save-timetable", methods=["POST"])
def save_timetable():
    db.session.add(Timetable(student_class=request.form.get("student_class"), day=request.form.get("day"),
                             period1=request.form.get("period1"), period2=request.form.get("period2"),
                             period3=request.form.get("period3"), period4=request.form.get("period4"),
                             period5=request.form.get("period5"), period6=request.form.get("period6"),
                             period7=request.form.get("period7"), period8=request.form.get("period8")))
    safe_commit()
    return redirect("/view-timetable")


@app.route("/save-announcement", methods=["POST"])
def save_announcement():
    db.session.add(Announcement(title=request.form.get("title"), message=request.form.get("message"),
                                sender=request.form.get("sender")))
    safe_commit()
    return redirect("/announcements")


@app.route("/announcements")
def announcements(): return render_template("announcements.html", announcements=Announcement.query.all())


@app.route("/send-message", methods=["POST"])
def send_message():
    db.session.add(ChatMessage(sender_email=request.form.get("sender"), receiver_email=request.form.get("receiver"),
                               message=request.form.get("message")))
    safe_commit()
    return redirect("/messages")


@app.route("/messages")
def messages(): return render_template("messages.html", chats=ChatMessage.query.all())


@app.route("/submit-tc-request", methods=["POST"])
def submit_tc_request():
    db.session.add(
        CertificateRequest(student_name=request.form.get("student_name"), roll_no=request.form.get("roll_no"),
                           request_type="TC", status="Pending"))
    safe_commit()
    return redirect("/my-requests")


@app.route("/submit-migration-request", methods=["POST"])
def submit_migration_request():
    db.session.add(
        CertificateRequest(student_name=request.form.get("student_name"), roll_no=request.form.get("roll_no"),
                           request_type="Migration", status="Pending"))
    safe_commit()
    return redirect("/my-requests")


@app.route("/my-requests")
def my_requests(): return render_template("my_requests.html", requests=CertificateRequest.query.all())


@app.route("/certificate-requests")
def certificate_requests(): return render_template("certificate_requests.html", requests=CertificateRequest.query.all())


@app.route("/approve-request/<int:id>")
def approve_request(id):
    req = CertificateRequest.query.get_or_404(id)
    req.status = "Approved"
    safe_commit()
    return redirect("/certificate-requests")


# ==========================================
# THE NEW ADVANCED FEATURES (BIODATA, VIDEOS, LIVE, CHAT)
# ==========================================

@app.route("/biodata", methods=["GET", "POST"])
def biodata():
    if 'user_role' not in session: return redirect("/")
    role = session['user_role']
    user = Student.query.get(session['user_id']) if role == "Student" else Teacher.query.get(session['user_id'])

    if request.method == "POST":
        user.dob = request.form.get("dob")
        user.blood_group = request.form.get("blood_group")
        user.address = request.form.get("address")
        if role == "Teacher": user.qualification = request.form.get("qualification")

        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                user.profile_pic = filename

        safe_commit()
        return redirect("/biodata")

    return render_template("biodata.html", user=user, role=role)


@app.route("/upload-material", methods=["GET", "POST"])
def upload_material():
    if request.method == "POST":
        m_type = request.form.get("type")
        if "file" in request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                if m_type == "note":
                    db.session.add(Notes(subject=request.form.get("subject"), title=request.form.get("title"),
                                         student_class=request.form.get("student_class"),
                                         division=request.form.get("division"), filename=filename))
                else:
                    db.session.add(
                        VideoClass(teacher_name=session.get('user_name'), subject=request.form.get("subject"),
                                   title=request.form.get("title"), student_class=request.form.get("student_class"),
                                   division=request.form.get("division"), filename=filename))
                safe_commit()
        return redirect("/upload-material")
    return render_template("upload_material.html")


@app.route("/class-materials")
def class_materials():
    if session.get('user_role') != "Student": return redirect("/")
    student = Student.query.get(session['user_id'])
    return render_template("class_materials.html", notes=Notes.query.filter_by(student_class=student.student_class,
                                                                               division=student.division).all(),
                           videos=VideoClass.query.filter_by(student_class=student.student_class,
                                                             division=student.division).all())


@app.route("/manage-live-classes", methods=["GET", "POST"])
def manage_live_classes():
    if request.method == "POST":
        db.session.add(LiveClass(teacher_name=session.get("user_name"), subject=request.form.get("subject"),
                                 title=request.form.get("title"), student_class=request.form.get("student_class"),
                                 division=request.form.get("division"), meeting_link=request.form.get("meeting_link"),
                                 schedule_time=request.form.get("schedule_time")))
        safe_commit()
        return redirect("/manage-live-classes")
    return render_template("manage_live_classes.html", classes=LiveClass.query.all())


@app.route("/mark-attendance-bulk", methods=["GET", "POST"])
def mark_attendance_bulk():
    if request.method == "POST":
        date = request.form.get("date")
        s_class = request.form.get("student_class")
        div = request.form.get("division")
        for student in Student.query.filter_by(student_class=s_class, division=div).all():
            status = request.form.get(f"status_{student.roll_no}")
            if status:
                existing = Attendance.query.filter_by(roll_no=student.roll_no, date=date).first()
                if existing:
                    existing.status = status
                else:
                    db.session.add(Attendance(roll_no=student.roll_no, student_class=s_class, division=div, date=date,
                                              status=status))
        safe_commit()
        return redirect("/mark-attendance-bulk")
    return render_template("mark_attendance_bulk.html", students=Student.query.all())


@app.route("/my-attendance-calendar")
def my_attendance_calendar():
    if session.get('user_role') != "Student": return redirect("/")
    student = Student.query.get(session['user_id'])
    return render_template("attendance_calendar.html", records=Attendance.query.filter_by(roll_no=student.roll_no).all())

@app.route("/chat-portal", methods=["GET", "POST"])
def chat_portal():
    if 'user_email' not in session: return redirect("/")
    my_email = session['user_email']

    if request.method == "POST":
        db.session.add(ChatMessage(sender_email=my_email, receiver_email=request.form.get("receiver_email"), message=request.form.get("message")))
        safe_commit()
        return redirect(f"/chat-portal?user={request.form.get('receiver_email')}")

    chat_partner = request.args.get("user")
    messages = []
    if chat_partner:
        messages = ChatMessage.query.filter(((ChatMessage.sender_email == my_email) & (ChatMessage.receiver_email == chat_partner)) | ((ChatMessage.sender_email == chat_partner) & (ChatMessage.receiver_email == my_email))).order_by(ChatMessage.timestamp).all()

    contacts = Teacher.query.all() if session.get('user_role') == "Student" else Student.query.all()
    return render_template("chat_portal.html", messages=messages, contacts=contacts, chat_partner=chat_partner)


# ==========================================
# NEW FEATURE: CLASS-WISE FEES
# ==========================================

@app.route("/manage-class-fees", methods=["GET", "POST"])
def manage_class_fees():
    if session.get('user_role') not in ['Admin', 'Principal']:
        return redirect("/")

    if request.method == "POST":
        s_class = request.form.get("student_class")
        fee_amt = int(request.form.get("base_fee"))

        # Check if the class already has a fee set. If yes, update it. If no, create it.
        existing_fee = ClassFee.query.filter_by(student_class=s_class).first()
        if existing_fee:
            existing_fee.base_fee = fee_amt
        else:
            db.session.add(ClassFee(student_class=s_class, base_fee=fee_amt))

        safe_commit()
        return redirect("/manage-class-fees")

    return render_template("manage_class_fees.html", class_fees=ClassFee.query.all())


# ==========================================
# NEW FEATURE: CLEAR NOTIFICATIONS
# ==========================================

@app.route("/delete-announcement/<int:id>")
def delete_announcement(id):
    # Only Admin or Principal should be able to delete announcements
    if session.get('user_role') in ['Admin', 'Principal']:
        Announcement.query.filter_by(id=id).delete()
        safe_commit()
    return redirect("/announcements")


@app.route("/clear-chat/<partner_email>")
def clear_chat(partner_email):
    # Deletes the entire conversation between you and that specific person
    my_email = session.get('user_email')
    if my_email:
        ChatMessage.query.filter(
            ((ChatMessage.sender_email == my_email) & (ChatMessage.receiver_email == partner_email)) |
            ((ChatMessage.sender_email == partner_email) & (ChatMessage.receiver_email == my_email))
        ).delete()
        safe_commit()
    return redirect("/chat-portal")


# ==========================================
# NEW FEATURE: AUTO-GENERATED REPORT CARDS
# ==========================================

@app.route("/generate-report/<roll_no>")
def generate_report(roll_no):
    if 'user_role' not in session: return redirect("/")

    # Fetch Student and their Marks
    student = Student.query.filter_by(roll_no=roll_no).first_or_404()
    marks = Marks.query.filter_by(roll_no=roll_no).all()

    # Mathematical Calculations
    total_marks = sum([m.marks for m in marks])
    max_marks = len(marks) * 100 if marks else 100
    percentage = (total_marks / max_marks) * 100 if marks else 0

    # Grading Logic
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F (Fail)"

    # Pass/Fail Status
    status = "Promoted" if percentage >= 50 else "Needs Improvement"

    return render_template("report_card.html",
                           student=student,
                           marks=marks,
                           total=total_marks,
                           max=max_marks,
                           percentage=round(percentage, 2),
                           grade=grade,
                           status=status)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)