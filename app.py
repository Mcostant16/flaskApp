from flask import Flask, render_template, request, redirect, url_for, jsonify
# JWT-based (e.g., with flask-jwt-extended)
from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from flask_login import login_required, current_user

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()



app = Flask(__name__)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Import models AFTER db is created
from models import UserSubmission

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
    user = UserSubmission.query.get_or_404(user_id)
    return render_template("results.html", user=user)

@app.route("/employees")
def employees():
    users = UserSubmission.query.all()
    for user in users:
        print(user)
    return render_template("employees.html", users=users)

@app.route("/table")
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



@app.route("/about")
def about():
    return "<h2>About this App</h2><p>Sample polished Flask application.</p>"

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if not exist
        app.config["SECRET_KEY"] = "your-secret-key-74232321"  # needed for CSRF protection
        csrf.init_app(app)
    app.run(host="127.0.0.1", port=5000, debug=True)