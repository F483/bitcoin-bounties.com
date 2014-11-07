#!/bin/bash

cd ~/www/
source env/bin/activate
python manage.py bounty_update_states
python manage.py userfund_update_cashes
python manage.py bounty_update_cashes


