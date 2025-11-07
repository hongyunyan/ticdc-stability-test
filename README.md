# TiCDC Stability Test

Automated stability testing system for TiCDC repository. This system creates multiple pull requests with minimal changes to test the stability of the master branch.

## Features

- Creates 10 PRs daily with minimal Makefile changes (one PR every 10 minutes)
- Monitors CI/CD test results automatically
- Closes PRs that pass tests and keeps failed ones for review
- Comprehensive logging and error handling
- Scheduled execution (daily at 8 PM UTC+8)
- Email and Feishu notifications for test results
- Staggered PR creation to avoid overwhelming CI systems

## Installation

1. Clone or download this project to your server
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Edit `config.env` file with your GitHub credentials and settings:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_github_username_here
REPO_OWNER=pingcap
REPO_NAME=ticdc
BASE_BRANCH=master

# PR Configuration
PR_COUNT=10
PR_TITLE_PREFIX="stability-test"
PR_BODY="Automated stability test PR - adding empty line to Makefile"

# Test Configuration
TEST_TIMEOUT_HOURS=2
CHECK_INTERVAL_MINUTES=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=stability_test.log

# Notification Configuration
EMAIL_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=your_email@gmail.com

FEISHU_ENABLED=false
FEISHU_WEBHOOK_URL=your_feishu_webhook_url
```

### GitHub Token Setup

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with the following permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)

### Email Notification Setup

1. For Gmail:
   - Enable 2-factor authentication
   - Generate an App Password (not your regular password)
   - Use the App Password in `EMAIL_PASSWORD`

2. For other email providers:
   - Update `SMTP_SERVER` and `SMTP_PORT` accordingly
   - Use your email credentials

### Feishu Notification Setup

1. Create a Feishu webhook:
   - Go to Feishu > Create Bot > Webhook
   - Copy the webhook URL to `FEISHU_WEBHOOK_URL`

## Usage

### Manual Test Run

To run the stability test immediately:

```bash
python scheduler.py run-now
```

### Start Daily Scheduler

To start the daily scheduler (runs at 8 PM UTC+8):

```bash
python scheduler.py schedule
```

### Direct Test Run

To run the test directly without scheduler:

```bash
python stability_test.py
```

## How It Works

1. **Staggered PR Creation**: Creates 10 PRs with 30-minute intervals to avoid overwhelming CI systems
   - Creates one PR every 30 minutes (total time: ~4.5 hours)
   - Each PR contains a small change to Makefile (adding an empty line)
   - Each PR triggers specific test commands instead of `/test all`
2. **Test Monitoring**: Monitors the CI/CD status of each PR after all PRs are created
3. **Result Processing**: 
   - Closes PRs and deletes branches for passed tests
   - Keeps failed PRs open for manual review
4. **Logging**: Records all activities in log files

### Test Commands

Each PR triggers the following specific test commands:
- `/test pull-cdc-kafka-integration-heavy`
- `/test pull-cdc-kafka-integration-light`
- `/test pull-cdc-mysql-integration-heavy`
- `/test pull-cdc-mysql-integration-light`
- `/test pull-cdc-storage-integration-heavy`
- `/test pull-cdc-storage-integration-light`
- `/test pull_cdc_mysql_integration_light_next_gen`

### PR Creation Timeline

- **Start Time**: 12:00 PM (UTC+8) daily
- **PR #1**: 12:00 PM
- **PR #2**: 12:30 PM
- **PR #3**: 1:00 PM
- ...
- **PR #10**: 4:30 PM
- **Test Monitoring**: Starts after all PRs are created (4:30 PM)
- **Report**: Sent when all tests complete or timeout (max 6 hours)

## Log Files

- `stability_test.log`: Main test execution logs
- `scheduler.log`: Scheduler operation logs

## Server Deployment

### Option 1: Using systemd (Recommended)

1. Copy the service file to systemd directory:

```bash
sudo cp ticdc-stability-test.service /etc/systemd/system/
```

2. Edit the service file to match your setup:

```bash
sudo nano /etc/systemd/system/ticdc-stability-test.service
```

Make sure to update:
- `User=hongyunyan` (your username)
- `WorkingDirectory=/home/hongyunyan/ticdc-stability-test` (your project path)

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ticdc-stability-test
sudo systemctl start ticdc-stability-test
```

4. Check service status:

```bash
sudo systemctl status ticdc-stability-test
```

5. View logs:

```bash
sudo journalctl -u ticdc-stability-test -f
```

### Option 2: Using cron (Simple)

1. Run the setup script:

```bash
./setup_cron.sh
```

This will automatically add a cron job to run daily at 12:00 PM (UTC+8).

2. Verify the cron job:

```bash
crontab -l
```

3. View logs:

```bash
tail -f stability_test.log
```

## Monitoring

Check the logs for monitoring:

```bash
# View recent logs
tail -f stability_test.log

# View scheduler logs
tail -f scheduler.log

# Check systemd service logs
sudo journalctl -u ticdc-stability-test -f
```

## Troubleshooting

### Common Issues

1. **GitHub API Rate Limiting**: The system includes delays between PR creations to avoid rate limiting
2. **Authentication Errors**: Ensure your GitHub token has the correct permissions
3. **Test Timeouts**: Adjust `TEST_TIMEOUT_HOURS` in config.env if tests take longer

### Debug Mode

To run with more verbose logging, modify `LOG_LEVEL=DEBUG` in config.env

## File Structure

```
ticdc-stability-test/
├── config.env              # Configuration file
├── requirements.txt        # Python dependencies
├── github_client.py        # GitHub API client
├── stability_test.py       # Main test logic
├── scheduler.py           # Task scheduler
├── README.md              # This file
├── stability_test.log     # Test execution logs
└── scheduler.log          # Scheduler logs
```

## Security Notes

- Keep your GitHub token secure and never commit it to version control
- The token should have minimal required permissions
- Consider using GitHub Apps for better security in production environments
