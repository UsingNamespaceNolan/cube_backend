# cube_backend

## Prepare the project

First create a python virtual environment:

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

Make database migrations:

```shell
python manage.py makemigrations
```

Perform the migrations:

```shell
python manage.py migrate
```

For the above two commands, you may need to add this option:

```shell
--settings=cube_project.settings.base
```

Run the server:

```shell
python manage.py runserver 8001 --settings=cube_project.settings.local
```

Voila
