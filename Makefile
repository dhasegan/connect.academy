install_pip:
	sudo apt-get install python-pip

install_venv: install_pip
	sudo pip install virtualenv

setup_venv:
	virtualenv venv

.ONESHELL:
install: setup_venv
	( \
		. venv/bin/activate; \
		sudo apt-get install libpq-dev python-dev -y; \
		sudo apt-get install rbenv -y; \
		sudo gem install sass -y; \
		sudo apt-get install graphviz libgraphviz-dev pkg-config -y; \
		pip install -r requirements.txt; \
		mkdir -p academy/db; \
		touch academy/db/database.db; \
		./manage.py syncdb --noinput; \
		./manage.py migrate guardian; \
		./manage.py schemamigration app --initial; \
		./manage.py migrate app --fake; \
		./manage.py shell_plus -c "Populator.populate_xsmall(); exit"; \
		./manage.py runserver; \
	)

clean:
	rm academy/db -r
	rm app/migrations/* 

#also, when installing locally (for development), make sure Connect's environment variables aren't in your ~/.bashrc 
