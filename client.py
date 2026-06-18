import socket, threading, tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from datetime import datetime
from crypto_utils import derive_key, encrypt_message, decrypt_message


HOST = '' #enter host id
PORT = 9999
PASSWORD = 'SuperSecret123'
SALT = b'12345678abcdefgh'

key = derive_key(PASSWORD, SALT)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

root = tk.Tk()
root.withdraw()
username = simpledialog.askstring("Username", "Enter your name:")
if not username:
    messagebox.showerror("Username required", "You must enter a username to continue.")
    root.destroy()
    exit()


client.send(encrypt_message(key, username))


root.deiconify()
root.title("🛡️ Encrypted Chat")
root.geometry("600x460")
current_theme = "dark"


themes = {
    "dark": {
        "bg": "#1e1e1e", "fg": "#ffffff",
        "chat_bg": "#2d2d2d", "chat_fg": "#dcdcdc",
        "entry_bg": "#3a3a3a", "entry_fg": "#ffffff",
        "button_bg": "#33ccff", "user_bg": "#2d2d2d"
    },
    "light": {
        "bg": "#f0f0f0", "fg": "#000000",
        "chat_bg": "#ffffff", "chat_fg": "#000000",
        "entry_bg": "#e0e0e0", "entry_fg": "#000000",
        "button_bg": "#4faaff", "user_bg": "#dddddd"
    }
}

def apply_theme(theme):
    t = themes[theme]
    root.configure(bg=t["bg"])
    chat_area.configure(bg=t["chat_bg"], fg=t["chat_fg"])
    entry.configure(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["entry_fg"])
    send_button.configure(bg=t["button_bg"])
    user_list.configure(bg=t["user_bg"], fg=t["fg"])
    theme_button.configure(bg=t["button_bg"], fg=t["fg"])


chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Consolas", 11))
chat_area.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)


bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

entry = tk.Entry(bottom_frame, font=("Consolas", 11))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_button = tk.Button(bottom_frame, text="Send", command=lambda: send())
send_button.pack(side=tk.LEFT)

theme_button = tk.Button(bottom_frame, text="🌗 Toggle Theme", command=lambda: toggle_theme())
theme_button.pack(side=tk.RIGHT)


user_list = tk.Listbox(root, height=3)
user_list.pack(fill=tk.X, padx=10, pady=(0, 10))

def update_users(msg):
    if "joined the chat" in msg or "left the chat" in msg:
        user_list.delete(0, tk.END)
        
        for client_name in sorted(set(u for u in all_usernames if u)):
            user_list.insert(tk.END, client_name)


all_usernames = set()

def send():
    msg = entry.get()
    if msg:
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_msg = f"[{timestamp}] {username}: {msg}"
        encrypted = encrypt_message(key, full_msg)
        client.send(encrypted)

        
        chat_area.config(state='normal')
        chat_area.insert(tk.END, full_msg + '\n')
        chat_area.yview(tk.END)
        chat_area.config(state='disabled')

        entry.delete(0, tk.END)

def receive():
    buffer = b""
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            buffer += data

            while True:
                try:
                    
                    decrypted = decrypt_message(key, buffer)
                    timestamped_msg = decrypted.strip()

                    chat_area.config(state='normal')
                    chat_area.insert(tk.END, timestamped_msg + "\n")
                    chat_area.yview(tk.END)
                    chat_area.config(state='disabled')

                    
                    if "joined the chat" in decrypted:
                        uname = decrypted.split()[0].strip("[]")
                        all_usernames.add(uname)
                        update_users(decrypted)
                    elif "left the chat" in decrypted:
                        uname = decrypted.split()[0].strip("[]")
                        all_usernames.discard(uname)
                        update_users(decrypted)

                    buffer = b""  
                    break
                except Exception as e:
                    
                    break
        except Exception as e:
            print(f"[ERROR] {e}")
            break

def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    apply_theme(current_theme)

entry.bind("<Return>", lambda e: send())
threading.Thread(target=receive, daemon=True).start()

apply_theme(current_theme)
root.mainloop()
client.close()
