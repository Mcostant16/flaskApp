
# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from models import UserSubmission, User  # import User here
from werkzeug.exceptions import BadRequest
from sqlalchemy import select



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


@login_manager.unauthorized_handler
def unauthorized():
    # Return JSON for API; for pages you could redirect
    if request.path.startswith("/api/"):
        return jsonify({"error": "Unauthorized"}), 401
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        role = request.form.get("role")
        record = UserSubmission(name=name, role=role)
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("results", user_id=record.id))
    return render_template("index.html")



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

@app.route("/table")
@login_required  # enforce authentication
def table():
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

    try:
        for r in rows:
            # validate and persist row...
            pass
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "DB error"}), 500


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
        next_url = request.args.get("next") or url_for("employees")
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
    with app.app_context():
        db.create_all()  # creates tables if not exist
    app.run(host="127.0.0.1", port=5000, debug=True)