
# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from models import UserSubmission, User, TrainingSubmissions  # import User here
from werkzeug.exceptions import BadRequest
from sqlalchemy import select, func
from datetime import datetime, timedelta
import os
from dateutil import parser as dtparse  # pip install python-dateutil (or parse manually)



csrf = CSRFProtect()
login_manager = LoginManager()

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-74232321"  # required for sessions + CSRF
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
csrf.init_app(app)
login_manager.login_view = "login"  # endpoint name defined below
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # standard loader for Flask-Login
    return db.session.get(User, int(user_id))

def print_submissions(*args, **kwargs):
    print("Training Submissions:")
    training = TrainingSubmissions.query.all()
    for row in training:
        print(row.id, row.email, row.user, row.training, row.train_date, row.status, row.created_at)
    print(training)


@login_manager.unauthorized_handler
def unauthorized():
    # Return JSON for API; for pages you could redirect
    if request.path.startswith("/api/"):
        return jsonify({"error": "Unauthorized"}), 401
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
# Only allow authenticated users to perform the write
        if not current_user.is_authenticated:
            # Option A: redirect to login with a message
            flash("Please log in to submit.", "warning")
            return redirect(url_for("login", next=url_for("index")))
            # Option B (API style): abort with 401/403
            # abort(401)  # or abort(403)
        name = request.form.get("name")
        role = request.form.get("role")
        if name:
            record = UserSubmission(name=name, role=role)
            db.session.add(record)
            db.session.commit()
            return redirect(url_for("results", user_id=record.id))

    # Recent rows for the table
    recent = (
        UserSubmission.query.order_by(UserSubmission.created_at.desc())
        .limit(5)
        .all()
    )

    # ---- Metrics for SQLite ----
    total_users = db.session.scalar(db.select(func.count(UserSubmission.id))) or 0

    # Count in current month using SQLite strftime('%Y-%m', column)
    this_month = db.session.scalar(
        db.select(func.count(UserSubmission.id)).where(
            func.strftime("%Y-%m", UserSubmission.created_at) ==
            datetime.utcnow().strftime("%Y-%m")
        )
    ) or 0

    last_7_days = db.session.scalar(
        db.select(func.count(UserSubmission.id)).where(
            UserSubmission.created_at >= datetime.utcnow() - timedelta(days=7)
        )
    ) or 0

    unique_roles = db.session.scalar(
        db.select(func.count(func.distinct(UserSubmission.role))).where(
            UserSubmission.role.isnot(None)
        )
    ) or 0

    metrics = {
        "total_users": total_users,
        "this_month": this_month,
        "last_7_days": last_7_days,
        "unique_roles": unique_roles,
    }
    
    # === GRAPH DATA ===

    # Submissions per month (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_rows = db.session.execute(
        db.select(
            func.strftime('%Y-%m', UserSubmission.created_at).label('month'),
            func.count(UserSubmission.id)
        )
        .where(UserSubmission.created_at >= six_months_ago)
        .group_by('month')
        .order_by('month')
    ).all()

    months = [row[0] for row in monthly_rows]
    counts = [row[1] for row in monthly_rows]

    # Last 7 days activity
    seven_days = datetime.utcnow() - timedelta(days=7)
    daily_rows = db.session.execute(
        db.select(
            func.strftime('%Y-%m-%d', UserSubmission.created_at).label('day'),
            func.count(UserSubmission.id)
        )
        .where(UserSubmission.created_at >= seven_days)
        .group_by('day')
        .order_by('day')
    ).all()

    daily_labels = [row[0] for row in daily_rows]
    daily_counts = [row[1] for row in daily_rows]

    # Role distribution
    role_rows = db.session.execute(
        db.select(
            UserSubmission.role,
            func.count(UserSubmission.id)
        )
        .where(UserSubmission.role.isnot(None))
        .group_by(UserSubmission.role)
    ).all()

    role_labels = [row[0] for row in role_rows]
    role_counts = [row[1] for row in role_rows]
    print("hello here are the counts", role_counts)
    print_submissions()


    return render_template(
        "index.html",
        recent=recent,
        metrics=metrics,
        months=months,
        counts=counts,
        daily_labels=daily_labels,
        daily_counts=daily_counts,
        role_labels=role_labels,
        role_counts=role_counts
)



@app.route("/results/<int:user_id>")
def results(user_id):
    user = db.session.get(UserSubmission, user_id)
    if not user:
        return "Not Found", 404
    return render_template("results.html", user=user)


@app.route("/employees")
@login_required  # enforce authentication
def employees():
    users = UserSubmission.query.all()
    for user in users:
        print(user)
    return render_template("employees.html", users=users)

@app.route("/table",methods=["GET", "POST"])
@login_required  # enforce authentication
def table():

    if request.method == "POST":
        name = request.form.get("name")
        role = request.form.get("role")
        record = UserSubmission(name=name, role=role)
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("results", user_id=record.id))
    
    users = UserSubmission.query.all()

   # Convert ORM objects  Python dicts
    data = [u.to_dict() for u in users]
    #return "<h2>Table HTML Page.</p>"
    return render_template("table.html",table_data=data)

@app.post("/api/employees/save")
@login_required  # enforce authentication
def save_employees():
    if not current_user.can_edit_employees:
        return jsonify({"error": "Forbidden"}), 403

    if not request.is_json:
        return jsonify({"error": "JSON required"}), 415

    rows = request.get_json()
    if not isinstance(rows, list):
        return jsonify({"error": "Array required"}), 400
    
    # Normalize to a list
    if isinstance(rows, dict) and 'submissions' in rows:
        items = rows['submissions']
    elif isinstance(rows, list):
        items = rows
    else:
        raise ValueError("JSON must be a list or an object with a 'submissions' array")

    rows = []
    for i, item in enumerate(items, start=1):
        try:
            email = item[0]
            user = str(item[1])
            training = item[2] 
            # Parse datetime (tolerant)
            train_date = dtparse.parse(item[3])
            status = item[4] 
        except KeyError as e:
            raise ValueError(f"Item {i} missing required field: {e}")

        rows.append(TrainingSubmissions(
            email=email,
            user=user,
            training=training,
            train_date=train_date,
            status=status
        ))

    # Bulk insert inside a transaction
    try:
        db.session.bulk_save_objects(rows)
        db.session.commit()
        return jsonify({"status": "success", "count": len(rows)}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "DB error"}), 500

@app.post("/employees/delete/<int:user_id>")
@login_required
def delete_user(user_id):
    user = db.session.get(UserSubmission, user_id)
    if not user:
        return "User not found", 404

    db.session.delete(user)
    db.session.commit()
    flash("Employee deleted successfully.", "success")

    return redirect(url_for("employees"))

# ---------- Auth routes ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("register.html"), 400

        # Check existing user
        if db.session.scalar(select(User).filter_by(email=email)):
            flash("Email already registered.", "warning")
            return render_template("register.html"), 400

        user = User(email=email)
        user.set_password(password)
        # Optional: first user becomes editor
        if db.session.scalar(select(db.func.count(User.id))) == 0:
            user.can_edit_employees = True

        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        remember = bool(request.form.get("remember"))

        user = db.session.scalar(select(User).filter_by(email=email))
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html"), 401

        login_user(user, remember=remember)
        flash("Logged in successfully.", "success")
        next_url = request.args.get("next") or url_for("index")
        return redirect(next_url)

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ---------- API route (unchanged logic, but now safe to use current_user) ----------


@app.route("/about")
def about():
    return "<h2>About this App</h2><p>Sample polished Flask application.</p>"

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    
# Avoid double-running with the dev reloader
    is_main_process = os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug
    if is_main_process:
        with app.app_context():
            db.create_all()  # creates tables if not exist
            print_submissions()
    app.run(host="127.0.0.1", port=5000, debug=True)