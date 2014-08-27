
SQLITE_FILE="development.db"
DITAA_DOCS := $(shell find | grep -i "doc/.*\.ditaa$$")

help:
	@echo "Usage: make <target> <option>=VALUE"
	@echo "  TARGETS                OPTIONS   "
	@echo "  docs                             "
	@echo "  django_startserver               "
	@echo "  bitcoin_startserver              "
	@echo "  bitcoin_stopserver               "
	@echo "  shell_python                     "
	@echo "  shell_sqlite                     "
	@echo "  clean                            "
	@echo "  messages_make                    "
	@echo "  messages_compile                 "

docs:
	@$(foreach DITAA,$(DITAA_DOCS), \
        ditaa $(DITAA) $(DITAA:.ditaa=.png);\
    )

django_startserver:
	@python manage.py runserver

counterparty_startserver:
	@counterpartyd --testnet --testcoin

bitcoin_startserver:
	@bitcoind -testnet -daemon -txindex

bitcoin_stopserver:
	@bitcoin-cli stop

shell_sqlite:
	sqlite3 $(SQLITE_FILE)

shell_python:
	python manage.py shell

messages_make:
	scripts/messages.sh makemessages

messages_compile:
	scripts/messages.sh compilemessages

clean:
	@find | grep -i ".*\.pyc$$" | xargs -r -L1 rm
	@find | grep -i ".*\.orig$$" | xargs -r -L1 rm
	@find | grep -i ".*\.swp$$" | xargs -r -L1 rm
	@find | grep -i ".*\.swo$$" | xargs -r -L1 rm
	@rm -rf bitcoin_bounties.egg-info
	@rm -rf build/*

