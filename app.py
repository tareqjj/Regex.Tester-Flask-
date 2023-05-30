from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import re


app = Flask(__name__)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///regex.db"
app.config["SECRET_KEY"] = "So-Seckrekt"
db.init_app(app)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regex = db.Column(db.String(50))
    text = db.Column(db.String(1024))
    result = db.Column(db.Boolean)


with app.app_context():
    db.create_all()


class Form(FlaskForm):
    regex = StringField(label="Regex", validators=[DataRequired()])
    text = StringField(label="Text", validators=[DataRequired()])


@app.route("/", methods=["GET", "POST"])
def index():
    form = Form()
    if request.method == "GET":
        return render_template("index.html", form=form)
    if request.method == "POST":
        if form.validate_on_submit():
            regexp = form.data["regex"]
            text = form.data["text"]
            if re.fullmatch(regexp, text) is not None:
                regex_match = True
            else:
                regex_match = False
            db.session.add(Record(regex=regexp, text=text, result=regex_match))
            db.session.commit()
            result_id = db.session.execute(db.select(Record.id).filter_by(regex=regexp, text=text)).scalar()
            return redirect(f"/result/{result_id}")


@app.route("/result/<int:result_id>")
def result(result_id):
    get_result = db.get_or_404(Record, result_id)
    return render_template("result.html", result=get_result)


@app.route("/history")
def history():
    result_list = db.session.execute(db.select(Record).order_by(Record.id.desc())).scalars()
    return render_template("history.html", result_list=result_list)


if __name__ == '__main__':
    app.run()
