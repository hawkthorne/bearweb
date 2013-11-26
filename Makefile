.PHONY: install serve databases blog manual migrate syncdb fmt test deploy collect debug
	
DJANGO_SETTINGS_MODULE := bearweb.settings.local
export DJANGO_SETTINGS_MODULE

venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -r requirements/local.txt
	. venv/bin/activate; pip install -r requirements/test.txt
	touch venv/bin/activate

install: venv
	. venv/bin/activate; pip install -r requirements/local.txt
	. venv/bin/activate; pip install -r requirements/test.txt

debug: venv
	. venv/bin/activate; python manage.py runserver

serve:
	. venv/bin/activate; honcho start -f Procfile.dev

syncdb: venv
	. venv/bin/activate; python manage.py syncdb

migrate: venv
	. venv/bin/activate; python manage.py migrate

init: venv
	. venv/bin/activate; python manage.py schemamigration core --initial
	. venv/bin/activate; python manage.py schemamigration games --initial


shell: venv
	. venv/bin/activate; python manage.py shell

collect: venv
	. venv/bin/activate; python manage.py collectstatic --noinput --dry-run

autoschema: venv
	. venv/bin/activate; python manage.py schemamigration --auto games
			
deploy: test
	git push origin master
	git push heroku master

blog:
	cd jekyll/blog && bundle install
	cd jekyll/blog && bundle exec jekyll build

css:
	cd compass && bundle install
	cd compass && exec compass watch .

fmt:
	. venv/bin/activate; flake8 blog bearweb games \
		--exclude "migrations"

test: fmt
	. venv/bin/activate; \
		coverage run manage.py test --settings=bearweb.settings.test


# Don't run the tests that take a long time
check: fmt
	. venv/bin/activate; DISABLE_SLOW=true coverage run manage.py \
		test --settings=bearweb.settings.test


databases:
	-@createdb -h localhost bearweb_local
	-@createdb -h localhost bearweb_test
