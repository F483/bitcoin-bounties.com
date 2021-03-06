
SQLITE_FILE="development.db"
DITAA_DOCS := $(shell find | grep -i "doc/.*\.ditaa$$")

help:
	@echo "Usage: make <target> <option>=VALUE"
	@echo "  TARGETS                OPTIONS   "
	@echo "  django_startserver               "
	@echo "  bitcoin_startserver              "
	@echo "  bitcoin_stopserver               "
	@echo "  shell                            "
	@echo "  clean                            "
	@echo "  messages                         "

django_startserver:
	@python manage.py runserver

counterparty_startserver:
	@counterpartyd --testnet --testcoin server

bitcoin_startserver:
	@bitcoind -testnet -daemon -txindex

bitcoin_stopserver:
	@bitcoin-cli stop

shell:
	@python manage.py shell

messages:
	scripts/messages.sh makemessages
	scripts/messages.sh compilemessages

clean:
	@find | grep -i ".*\.pyc$$" | xargs -r -L1 rm
	@find | grep -i ".*\.swp$$" | xargs -r -L1 rm
	@find | grep -i ".*\.swo$$" | xargs -r -L1 rm
	@rm -rf bitcoin_bounties.egg-info
	@rm -rf build/*


# DEBUGGING
# pip install pudb # install debugger
# import pudb; pu.db # set break point
