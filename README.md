# WaiverStevie Demo Project

## Quickstart

See [flask's documentation](https://flask.palletsprojects.com/en/1.1.x/installation/#python-version) for installing flask and using a virtual environment

```bash
# See https://flask.palletsprojects.com/en/1.1.x/installation/#python-version for installing flask
pip install -r requirements.txt
# If you don't have flask installed see the above documentation
export FLASK_APP=main.py; export FLASK_ENV=development; flask run
```

## Using a Virtual Environment (optional)

A virtual environment makes sure all dependencies are local to this project as opposed to installed globally on the operating system; it encapsulates everything this project needs

```bash
python3 -m venv venv
chmod +x venv/bin/activate # makes the virtual env executable
```

And then, any terminal connected to this project, make sure to run:

```bash
source venv/bin/activate
```

Finally install requirements:

```bash
pip3 install -r requirements.txt
```
