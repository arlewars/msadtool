import tkinter as tk
from tkinter import messagebox
#import ms_active_directory
from ms_active_directory import ADDomain
from ldap3 import NTLM
import threading

DEBUG = True

server_map = {
    'LUV': 'LUV.AD.SWACORP.COM',
    'QAAD': 'QAADLUV.SWACORP.COM',
    'DEVAD': 'DEVAD.SWACORP.COM'
}

bind_paths = {
    "LUV": [
        "cn={username},ou=users,ou=field,ou=swaco,dc=luv,dc=ad,dc=swacorp,dc=com",
        "cn={username},ou=security operations,ou=security,ou=admin,dc=luv,dc=ad,dc=swacorp,dc=com"
    ],
    "QAAD": [
        "cn={username},ou=users,ou=field,ou=swaco,dc=qaad,dc=qaad,dc=swacorp,dc=com",
        "cn={username},ou=security operations,ou=security,ou=admin,dc=qaad,dc=qaad,dc=swacorp,dc=com"
    ],
    "DEVAD": [
        "cn={username},ou=users,ou=field,ou=swaco,dc=devad,dc=devad,dc=swacorp,dc=com",
        "cn={username},ou=security operations,ou=security,ou=admin,dc=devad,dc=devad,dc=swacorp,dc=com"
    ]
}

def get_user_data(username, ad):
    """Query user data from Active Directory."""
    if DEBUG:
        print(f"Querying user data for {username}")
    user = ad.find_user_by_name(username)
    if user:
        return user['displayName'], user['mail'], user['telephoneNumber']
    return None

def query_users():
    user1_name = entry_user1.get()
    user2_name = entry_user2.get()
    username = entry_username.get()
    password = entry_password.get()
    env = env_var.get()

    if DEBUG:
        print(f"Configuration:\nUsername: {username}\nEnvironment: {env}\nServer: {server_map[env]}")

    server = server_map[env]
    domain = ADDomain(server)

    # Attempt to bind with provided credentials or fallback to alternative paths
    ad = None
    try:
        ad = domain.create_session_as_user(username, password)
    except Exception as e:
        if DEBUG:
            print(f"Initial bind failed: {e}. Trying alternative bind paths...")
        for path in bind_paths[env]:
            try:
                ad = domain.create_session_as_user(path.format(username=username), password)
                break
            except Exception as e:
                if DEBUG:
                    print(f"Bind with path {path.format(username=username)} failed: {e}")
                continue

    if not ad:
        messagebox.showerror("Error", "Failed to bind to Active Directory.")
        return

    # Use threads to query both users simultaneously
    def query_user1():
        nonlocal user1_data
        user1_data = get_user_data(user1_name, ad)

    def query_user2():
        nonlocal user2_data
        user2_data = get_user_data(user2_name, ad)

    user1_data = None
    user2_data = None

    # Create threads to query the users
    thread1 = threading.Thread(target=query_user1)
    thread2 = threading.Thread(target=query_user2)

    # Start both threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()

    # Update UI with results
    if user1_data and user2_data:
        result_text.set(f"User 1:\nName: {user1_data[0]}\nEmail: {user1_data[1]}\nPhone: {user1_data[2]}\n\n"
                        f"User 2:\nName: {user2_data[0]}\nEmail: {user2_data[1]}\nPhone: {user2_data[2]}")
    else:
        messagebox.showerror("Error", "One or both users not found.")

# Set up the GUI
root = tk.Tk()
root.title("AD Query Tool")

label_username = tk.Label(root, text="AD Username:")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()

label_password = tk.Label(root, text="AD Password:")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

label_env = tk.Label(root, text="Environment:")
label_env.pack()
env_var = tk.StringVar(value='LUV')
env_menu = tk.OptionMenu(root, env_var, *server_map.keys())
env_menu.pack()

label_user1 = tk.Label(root, text="Username 1:")
label_user1.pack()
entry_user1 = tk.Entry(root)
entry_user1.pack()

label_user2 = tk.Label(root, text="Username 2:")
label_user2.pack()
entry_user2 = tk.Entry(root)
entry_user2.pack()

query_button = tk.Button(root, text="Query", command=query_users)
query_button.pack()

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text)
result_label.pack()

root.mainloop()