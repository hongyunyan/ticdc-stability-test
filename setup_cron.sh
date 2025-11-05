#!/bin/bash

# Setup cron job for TiCDC Stability Test
# This script will add a cron job to run the test daily at 12:00 PM (UTC+8)

echo "Setting up cron job for TiCDC Stability Test..."

# Get the current directory
CURRENT_DIR=$(pwd)

# Create the cron job entry (runs at 12:00 PM UTC+8, which is 4:00 AM UTC)
CRON_JOB="0 4 * * * cd $CURRENT_DIR && /usr/bin/python3 scheduler.py run-now >> stability_test.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"
echo "The test will run daily at 12:00 PM (UTC+8)"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (then delete the line with ticdc-stability-test)"
