python manage.py makemigrations --settings=cube_project.settings.base &&
python manage.py migrate --settings=cube_project.settings.base &&
python manage.py makemigrations cube_app --settings=cube_project.settings.base &&
python manage.py migrate cube_app --settings=cube_project.settings.base &&
python manage.py runserver 8001 --settings=cube_project.settings.local