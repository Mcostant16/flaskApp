from flask import Flask, render_template, request, redirect, url_for
from extensions import db

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




@app.route("/about")
def about():
    return "<h2>About this App</h2><p>Sample polished Flask application.</p>"

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if not exist
    app.run(host="127.0.0.1", port=5000, debug=True)