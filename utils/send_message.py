import subprocess

def send_text_message(message, phone_number="252-571-5303"):
    applescript_command = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    subprocess.run(['osascript', '-e', applescript_command])

# Example usage:
send_text_message("Test message from Python!")