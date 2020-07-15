from flask import render_template, redirect, g, Flask, request, url_for, session
from sqlite3 import dbapi2 as sqlite3
from os import path
import requests
app = Flask(__name__)


app.config.from_pyfile('config.py')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_file = app.config["DATABASE"]
        exists = path.isfile(db_file)
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        if not exists:
            qry = open('schema.sql', 'r').read()
            c = db.cursor()
            c.executescript(qry)
            db.commit()
            c.close()

    # Make sure database has tables
    return db


def cursor_to_dict_array(cur):
    columns = [column[0] for column in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=["GET"])
def base():
    if not session.get('logged_in'):
        return redirect("/login")
    return redirect("/home")


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
    # load completed projects
    db = get_db()
    cur = db.execute('select * from projects where is_complete=0')
    entries = cursor_to_dict_array(cur)
    # render home page with completed projects
    return render_template('home.html', type="active", entries=entries)


@app.route('/home/completed')
def home_completed():
    if not session.get('logged_in'):
        return redirect("/login")
    # load completed projects
    db = get_db()
    cur = db.execute('select * from projects where is_complete=1')
    entries = cursor_to_dict_array(cur)
    # render home page with completed projects
    return render_template('home.html', type="completed", entries=entries)


@app.route("/projects", methods=["POST"])
def add_project():
    if not session.get('logged_in'):
        return redirect("/login")
    contact_email = request.form.get('contact_email', type=str)
    contact_name = request.form.get('contact_name', type=str)
    quote_cost = request.form.get('quote_dollars', type=int)
    is_complete = request.form.get('is_complete')

    # break out first and last name if appropriate
    name_arr = contact_name.split(" ", 1)
    contact_first_name = name_arr[0]
    contact_last_name = name_arr[1] if len(name_arr) > 1 else ""

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'insert into projects (contact_email,contact_name,contract_type,quote_dollars,is_complete) values (?,?,?, ?, ?)',
        (
            contact_email,
            contact_name,
            'hourly' if request.form.get(
                'contract_type') == "hourly" else "milestone",
            quote_cost,
            0 if not is_complete else 1
        )
    )
    project_id = cursor.lastrowid
    db.commit()
    db.close()
    # Code for hitting WaiverStevie API
    r = requests.post('https://app.waiverstevie.com/api/v2/forms/' + app.config['WS_CONTRACT_ID'] + "/envelopes?api_key=" + app.config['WS_API_KEY'], json={
        "tags": [
            {
                "key": "project_id",
                "value": str(project_id)
            }
        ],
        "signers": [
            {

                "email": app.config['DEV_EMAIL'],
                "first_name": app.config["DEV_FIRST_NAME"],
                "last_name": app.config["DEV_LAST_NAME"],
                "prefilled_fields": [
                    {
                        "label": "Cost",
                        "value": "$" + str(quote_cost)
                    }
                ]
            },
            {
                "email": contact_email,
                "first_name": contact_first_name,
                "last_name": contact_last_name
            }
        ],
        'preset_values': [
            {

            }
        ],
        "send_email": True
    })

    return redirect(url_for('home'))


@app.route("/home/projects/<int:project_id>", methods=["GET"])
def edit_project_page(project_id):
    if not session.get('logged_in'):
        return redirect("/login")
    # Load particular project
    db = get_db()
    cur = db.execute("select * from projects where id=?", (int(project_id),))
    entries = cursor_to_dict_array(cur)
    if len(entries) == 0:
        return redirect('/home')

    # Return page
    return render_template('edit_form.html', project=entries[0])


@app.route("/projects/contract-check/<int:project_id>", methods=["GET"])
def manually_check_for_signature(project_id):
    r = requests.get("https://app.waiverstevie.com/api/v2/forms/{}/envelopes?api_key={}&tag_project_id={}".format(
        app.config['WS_CONTRACT_ID'], app.config['WS_API_KEY'], project_id))
    body = r.json()
    if len(body["data"]) > 0:
        # Update the database accordingly
        signers = body["data"][len(body["data"]) - 1]["signers"]
        final_pdf = signers[len(signers)-1]["signed_pdf"]
        if final_pdf:
            db = get_db()
            db.execute(
                '''UPDATE projects SET signed_pdf=? where id=?''',
                (
                    final_pdf,
                    project_id
                )
            )
            db.commit()
            db.close()
    return redirect(url_for('home'))


@app.route("/projects/edit/<int:project_id>", methods=["POST"])
def edit_project(project_id):
    if not session.get('logged_in'):
        return redirect("/login")
    # Save the information into the database
    db = get_db()
    db.execute(
        '''UPDATE projects SET contact_email=?, contact_name=?, contract_type=?, quote_dollars=?, is_complete=? where id=?''',
        (
            request.form.get('contact_email', type=str),
            request.form.get('contact_name', type=str),
            'hourly' if request.form.get(
                'contract_type') == "hourly" else "milestone",
            request.form.get('quote_dollars', type=int),
            0 if not request.form.get('is_complete') else 1,
            project_id
        )
    )
    db.commit()
    db.close()

    return redirect(url_for('home'))
