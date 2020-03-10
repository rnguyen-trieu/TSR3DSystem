# TSR3DSystem

## Clone the repository
You can clone it directly from
[rnguyen-trieu/TSR3DSystem](https://github.com/rnguyen-trieu/TSR3DSystem.git)
```bash
git clone https://github.com/rnguyen-trieu/TSR3DSystem.git
```

## Setup development environment
Enter the project directory
```bash
cd TSR3DSystem
```
Lets create a virtual environment for our project
```bash
python3 -m venv env
source env/bin/activate
```

## Install requirements
All the requirements are mentioned in the file `requirements.txt`.
```bash
pip install -r requirements.txt
```


## Setup database
App development is done using `postgresql` database.
Assuming you are inside the directory where `manage.py` also present
```bash
python manage.py makemigrations
python manage.py migrate
```
Collect all the static files for fast serving
```bash
python manage.py collectstatic
```

## Run server
```bash
python manage.py runserver
```
