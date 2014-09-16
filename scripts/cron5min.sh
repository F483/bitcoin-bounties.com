#!/bin/bash

python ~/www/manage.py bounty_update_states
python ~/www/manage.py userfund_update_cashes
python ~/www/manage.py bounty_update_cashes

