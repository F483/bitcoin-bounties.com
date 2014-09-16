#!/bin/bash

python ~/www/manage.py claim_process_payouts
python ~/www/manage.py userfund_process_refunds
python ~/www/manage.py counterparty_squash

