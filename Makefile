
APP=""
BITCOIND="bitcoind"
SQLITE_FILE="development.db"
DITAA_DOCS := $(shell find | grep -i "doc/.*\.ditaa$$")

help:
	@echo "Usage: make <target> <option>=VALUE"
	@echo "  TARGETS                OPTIONS   "
	@echo "  docs                             "
	@echo "  runserver_django                 "
	@echo "  runserver_bitcoin                "
	@echo "  py_shell                         "
	@echo "  db_sync                          "
	@echo "  db_migration_create    APP       "
	@echo "  db_migration_apply     APP       "
	@echo "  db_shell_sqlite                  "
	@echo "  clean                            "
	@echo "  clean_vim                        "
	@echo "  makemessages                     "
	@echo "  compilemessages                  "

docs:
	@$(foreach DITAA,$(DITAA_DOCS), \
        ditaa $(DITAA) $(DITAA:.ditaa=.png);\
    )

runserver_django:
	python manage.py runserver

runserver_bitcoin:
	$(BITCOIND) -testnet -server -txindex

db_shell_sqlite:
	sqlite3 $(SQLITE_FILE)

db_migration_create:
	python manage.py schemamigration $(APP) --auto

db_migration_apply:
	python manage.py migrate $(APP)

db_sync:
	python manage.py syncdb

py_shell:
	python manage.py shell

makemessages:
	scripts/messages.sh makemessages

compilemessages:
	scripts/messages.sh compilemessages

clean:
	@find | grep -i ".*\.pyc$$" | xargs -r -L1 rm
	@find | grep -i ".*\.orig$$" | xargs -r -L1 rm
	@find | grep -i ".*\.swp$$" | xargs -r -L1 rm
	@find | grep -i ".*\.swo$$" | xargs -r -L1 rm

