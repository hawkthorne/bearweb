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

worker: venv
	. venv/bin/activate; python manage.py celery worker --loglevel=info

serve:
	. venv/bin/activate; honcho start -f Procfile.dev

syncdb: venv
	. venv/bin/activate; python manage.py syncdb

migrate: venv
	. venv/bin/activate; python manage.py migrate games

init: venv
	#. venv/bin/activate; python manage.py schemamigration core --initial
	. venv/bin/activate; python manage.py schemamigration games --initial


shell: venv
	. venv/bin/activate; python manage.py shell

collect: venv
	. venv/bin/activate; python manage.py collectstatic --noinput --dry-run

autoschema: venv
	. venv/bin/activate; python manage.py schemamigration --auto games

flush: venv
	. venv/bin/activate; python manage.py flush
				
deploy: test
	git push origin master
	git push heroku master
	heroku run python manage.py migrate
	say -v "Good News" "Deployment is complete"

lovesdk: 
	rm -rf games/build/love-sdk
	cp -r ../stackmachine.love/stackmachine games/build/love-sdk

blog:
	cd jekyll/blog && bundle install
	cd jekyll/blog && bundle exec jekyll build

css:
	cd compass && bundle install
	cd compass && exec compass watch .

fmt:
	. venv/bin/activate; find blog core bearweb games -name "*.py" | grep -v "migrations" | xargs -I {} pep8ify -n -w {}


pep8:
	. venv/bin/activate; flake8 blog core bearweb games \
		--exclude "migrations"

test: pep8
	. venv/bin/activate; \
		coverage run manage.py test --settings=bearweb.settings.test -v 2

love8:
	games/build/love8/osx/love.app/Contents/MacOS/love games/build

love9:
	games/build/love9/osx/love.app/Contents/MacOS/love games/build



pipeline: clean test
	cd media/$(shell ls media | sort -n | head -1)/0.1.0 && unzip -qq foo-osx-0.1.0.zip
	open media/$(shell ls media | sort -n | head -1)/0.1.0/Foo.app

clean:
	rm -rf media
	mkdir -p media	

# Don't run the tests that take a long time
check: pep8
	. venv/bin/activate; DISABLE_SLOW=true coverage run manage.py \
		test --settings=bearweb.settings.test -v 2

databases:
	-@createdb -h localhost bearweb_local
	-@createdb -h localhost bearweb_test
