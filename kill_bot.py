import os
import signal
import subprocess

def find_and_kill_process(process_name):
    # Find the process ID (PID) using ps and grep
    try:
        result = subprocess.run(['pgrep', '-f', process_name], stdout=subprocess.PIPE)
        pids = result.stdout.decode().strip().split('\n')

        if not pids or pids == ['']:
            print(f"No running process found for: {process_name}")
            return

        print(f"Found {len(pids)} process(es) for {process_name}: {', '.join(pids)}")

        # Kill each process
        for pid in pids:
            print(f"Killing process {pid}...")
            os.kill(int(pid), signal.SIGTERM)
            print(f"Process {pid} terminated.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with your process name or part of the command
    process_name = "bot_schedule.py"
    find_and_kill_process(process_name)