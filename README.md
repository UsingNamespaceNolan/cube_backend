# cube_backend

## Prepare the project

Create two files in the root of the repository, .env and db.sqlite3. In your env file put a secret key:

```
DJANGO_SECRET_KEY='your-secret-key'
```

Create a python virtual environment:

```shell
python -m venv .venv
```

Activate the venv:

```shell
source .venv/bin/activate
```

You can verify the venv is active with:

```source
which python  # this should print a path to the venv python interpreter
```

Install dependencies with:

```shell
pip install -r requirements
```

Make default database migrations:

```shell
python manage.py makemigrations --settings=cube_project.settings.base
```

Perform the default migrations:

```shell
python manage.py migrate --settings=cube_project.settings.base
```

Do the same thing with the app specific models:

```shell
python manage.py makemigrations cube_app --settings=cube_project.settings.base
```

```shell
python manage.py migrate cube_app --settings=cube_project.settings.base
```

## Run the server:

```shell
python manage.py runserver 8001 --settings=cube_project.settings.local
```

## In production:

```shell
python manage.py runserver 8001 --settings=cube_project.settings.production
```

Voila
