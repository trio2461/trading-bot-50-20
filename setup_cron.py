# setup_cron.py
import os
import subprocess
import sys

# Get the current working directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the paths relative to the current directory
python_path = os.path.join(current_directory, "env/bin/python")
script_path = os.path.join(current_directory, "bot.py")
log_path = os.path.join(current_directory, "error_log.txt")

# Define the cron job command
cron_command = f"30 9-16 * * 1-5 {python_path} {script_path} >> {log_path} 2>&1"

def setup_cron_job():
    # Check if the cron job already exists
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    current_crontab = result.stdout

    # Add the cron job if it doesn't exist
    if cron_command not in current_crontab:
        with open('my_crontab', 'w') as f:
            if current_crontab:
                f.write(current_crontab)
            f.write(cron_command + '\n')

        subprocess.run(['crontab', 'my_crontab'])
        os.remove('my_crontab')
        print("Cron job added successfully.")
    else:
        print("Cron job already exists.")

def remove_cron_job():
    # Get the current cron jobs
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    current_crontab = result.stdout

    # Remove the cron job if it exists
    if cron_command in current_crontab:
        new_crontab = current_crontab.replace(cron_command + '\n', '')
        with open('my_crontab', 'w') as f:
            f.write(new_crontab)

        subprocess.run(['crontab', 'my_crontab'])
        os.remove('my_crontab')
        print("Cron job removed successfully.")
    else:
        print("Cron job does not exist.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--remove':
        remove_cron_job()
    else:
        setup_cron_job()