#!/bin/bash
cd /home/remote-host/proj-folder
source venv/bin/activate
python manage.py unban
echo "$(date) cron here un-banning users"

# in cron -e
# unban
#25 21 * * *  path to unban.sh >> path to cron_unban.log

# success new letter
#45 * * * *  path to greet.sh >> path to celery.log