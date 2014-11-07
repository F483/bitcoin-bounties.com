#!/bin/bash

cd ~/www/
source env/bin/activate
python manage.py claim_process_payouts
python manage.py userfund_process_refunds
python manage.py counterparty_squash

