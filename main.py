from flask import render_template, redirect, g, Flask, request, url_for, session
from sqlite3 import dbapi2 as sqlite3

app = Flask(__name__)


app.config.from_pyfile('config.py')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid Username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid Username"

        else:
            session['logged_in'] = True
            return redirect(url_for('home'))

    return render_template('login.html', error=error)


# @app.route('/signup')
# def signup():
#     if request.method == "POST":
#         # get body, validate signup.html
#         signup = request.form.to_dict()
#         if signup["password"] == signup["confirm_password"]

#     else:
#         return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect("/login")


@app.route('/home')
def home():
    return redirect("/home/active")


@app.route('/home/active')
def home_active():
    if not session.get('logged_in'):
        return redirect("/login")

    db = get_db()
    cur = db.execute('select * from projects where is_complete=0')
    columns = [column[0] for column in cur.description]
    entries = [dict(zip(columns, row)) for row in cur.fetchall()]

    return render_template('home.html', type="active", entries=entries)


@app.route('/home/completed')
def home_completed():
    if not session.get('logged_in'):
        return redirect("/login")

    db = get_db()
    cur = db.execute('select * from projects where is_complete=1')
    columns = [column[0] for column in cur.description]
    entries = [dict(zip(columns, row)) for row in cur.fetchall()]

    return render_template('home.html', type="completed", entries=entries)


@app.route("/projects", methods=["POST"])
def add_project():
    if not session.get('logged_in'):
        return redirect("/login")
    # Save the information into the database
    try:
        db = get_db()
        db.execute(
            'insert into projects (contact_email,contact_name,contract_type,quote_dollars,is_complete) values (?,?,?, ?, ?)',
            (
                request.form.get('contact_email', type=str),
                request.form.get('contact_name', type=str),
                'hourly' if request.form.get(
                    'contract_type') == "hourly" else "milestone",
                request.form.get('quote_dollars', type=int),
                0 if not request.form.get('is_complete') else 1
            )
        )
        db.commit()
        db.close()
    except:
        return "Error"
    return redirect(url_for('home'))


@app.route("/home/projects/<int:project_id>")
def edit_project(project_id):
    # not sure what's supposed to be in here yet need to figure out how to reference specific project
    if not session.get('logged_in'):
        return redirect("/login")
    try:
        db = get_db()
        # want curr to hold the information for a project
        curr = db.execute("select * from projects where id='%d'" % project_id)
        return render_template('edit_form.html')
    except:
        return "Error"
