OS := $(shell uname)

install_pip:
ifeq ($(OS),Darwin)
	sudo easy_install pip
else
	sudo apt-get install python-pip
endif

install_psql:
ifeq ($(OS),Darwin)
	brew install postgresql
else
	sudo apt-get install libpq-dev python-dev -y
endif

install_rbenv:
ifeq ($(OS),Darwin)
	brew install rbenv
else
	sudo apt-get install rbenv -y
endif

install_sass: install_rbenv
	sudo gem install sass
	git submodule update

install_graphviz:
ifeq ($(OS),Darwin)
	brew install graphviz
else
	sudo apt-get install graphviz libgraphviz-dev -y
endif

install_pkg-config:
ifeq ($(OS),Darwin)
	brew install pkg-config
else
	sudo apt-get install pkg-config -y
endif

install_venv: install_pip
	pip install virtualenv

venv: install_venv
	virtualenv venv --distribute

install: install_psql install_sass install_graphviz install_pkg-config install_venv

.ONESHELL:
setup: install venv
	( \
		. venv/bin/activate; \
		pip install -r requirements.txt; \
		mkdir -p academy/db; \
		./manage.py syncdb --noinput; \
		./manage.py migrate guardian; \
		./manage.py schemamigration app --initial; \
		./manage.py migrate app --fake; \
		echo "Populator.populate_xsmall(); exit" | ./manage.py shell_plus; \
	)

clean:
	rm academy/db -r
	rm app/migrations/* 
