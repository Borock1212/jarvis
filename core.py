import json
import re
import subprocess
import tkinter.messagebox as messagebox

from history import history, history_file
from config import client
from mail_utils import check_inbox
from web_utils import search_web
from screen_utils import read_screen_text

# === Execute command and query GPT ===
def execute_command(command_text):
    response_text = ""
    try:
        history.append({"role": "user", "content": command_text})
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        gpt_reply = chat_response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": gpt_reply})

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        if "[mail]" in gpt_reply.lower():
            result = check_inbox()
            interpreted = result
        else:
            interpreted = interpret_response(gpt_reply)
        response_text = f"Yuki:\n{gpt_reply}\n\n{interpreted}"
    except Exception as e:
        response_text = f"Error: {e}"

    return response_text

# === Interpret GPT commands ===
def interpret_response(response_text):
    actions = []
    lines = response_text.strip().split("\n")
    for line in lines:
        if match := re.match(r"\[open:(.+?)\]", line):
            url = match.group(1)
            subprocess.Popen(["start", url], shell=True)
            actions.append(f"\u2714 Opened website: {url}")

        elif match := re.match(r"\[reminder:(.+?)\]", line):
            note = match.group(1)
            with open("reminder.txt", "a", encoding="utf-8") as f:
                f.write(note + "\n")
            actions.append(f"\u2714 Added reminder: {note}")

        elif match := re.match(r"\[run:(.+?)\]", line):
            program = match.group(1)
            if any(cmd in program.lower() for cmd in ["del", "delete", "uninstall", "remove"]):
                confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to execute delete command: {program}?")
                if not confirm:
                    actions.append(f"\u274C Cancelled: {program}")
                    continue
            try:
                subprocess.Popen([program], shell=True)
                actions.append(f"\u2714 Launched program: {program}")
            except Exception as e:
                actions.append(f"Error running {program}: {e}")

        elif match := re.match(r"\[search:(.+?)\]", line):
            query = match.group(1)
            search_result = search_web(query)
            actions.append(search_result)

        elif "[screenread]" in response_text.lower() or "read screen" in response_text.lower():
            screen_text = read_screen_text()
            actions.append(f"📋 Screen text:\n{screen_text}")

        elif "[mail]" in line.lower() or "mail" in line.lower() or "inbox" in line.lower():
            mail_text = check_inbox()
            actions.append(f"📬 Mail:\n{mail_text}")

    return "\n".join(actions) if actions else "\u26A0 No recognized commands"

def check_early_triggers(command):
    command = command.lower()
    if any(keyword in command for keyword in ["mail", "inbox", "letters"]):
        return check_inbox()
    if any(keyword in command for keyword in ["read screen", "screenread"]):
        return read_screen_text()
    return None
