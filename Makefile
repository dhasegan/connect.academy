install_pip:
	echo "Installing pip..."
	sudo apt-get install python-pip

install_venv: install_pip
	echo "Installing Virtualenv"
	sudo pip install virtualenv

activate_venv: install_venv
	echo "Activating venv"
	virtualenv venv
	. venv/bin/activate

install_psycopg2: activate_venv
	echo "Installing psycopg2..."
	sudo apt-get install libpq-dev python-dev

install_graphviz: install_psycopg2
	sudo apt-get install graphviz libgraphviz-dev pkg-config

install_other_requirements: install_graphviz
	echo "Installing other requirements with pip"
	sudo pip install -r requirements.txt

create_db: install_other_requirements
	echo "Creating database..."
	mkdir academy/db && touch academy/db/database.db

sync_db: create_db
	echo "Synchronizing database..."
	./manage.py syncdb --noinput && ./manage.py migrate guardian

initial_migration: sync_db
	echo "Creating initial migration and applying it (fake)..."
	./manage.py schemamigration app --initial && ./manage.py migrate app --fake

launch_shell:	initial_migration
	echo "Launching shell"
	./manage.py shell_plus

run_server: launch_shell
	echo "Running server"
	./manage.py runserver

all: run_server


