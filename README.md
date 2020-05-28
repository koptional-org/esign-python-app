# WaiverStevie Demo Project

## Getting started

You'll need to create a virtualenv first thing. A virtual environment makes sure all dependencies are local to this project as opposed to installed globally in the OS; it encapsulates everything this project in particular needs

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

## Running the app

### If the address is already in use, change the port to something else like 5002

```bash
# keep a terminal open where this is running
export FLASK_APP=main.py; export FLASK_ENV=development; flask run --host=0.0.0.0 --port=5001
```
