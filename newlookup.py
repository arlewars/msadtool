import tkinter as tk
from tkinter import messagebox
import ms_active_directory
from ms_active_directory import ADDomain
from ldap3 import NTLM

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

#Common Name Lookup
#user_cn = 'John Doe'
#users = session.find_users_by_common_name(user_cn, ['employeeID'])
#group_dn = 'operations managers'
#groups = session.find_groups_by_common_name(group_dn, ['gidNumber'])
#Attribute Lookup
#desired_employee_type = 'temporary'
#users = session.find_users_by_attribute('employeeType', desired_employee_type, ['employeeID'])
#desired_group_manager = 'Alice P Hacker'
#groups = session.find_groups_by_attribute('managedBy', desired_group_manager, ['gidNumber'])
# Generic Name Lookup
#user_name = 'John Doe'
#user = session.find_user_by_name(user_name, ['employeeID'])
#group_name = 'operations managers'
#groups = session.find_groups_by_name(group_name, ['gidNumber'])
# SAM Lookup
#user = session.find_user_by_sam_name('user1', ['employeeID'])
#group = session.find_group_by_sam_name('group1', ['gidNumber'])


def get_user_data(username, env, ad):
    if DEBUG:
        print(f"Querying user data for {username} in {env}")
    user = ad.find_user_by_name(username)
    if user:
        return user['displayName'], user['mail'], user['telephoneNumber']
    else:
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

    # Attempt to bind with provided credentials
    try:
        if DEBUG:
            print(f"Attempting to bind with username: {username}")
        ad = domain.create_session_as_user(username, password)
    except Exception as e:
        if DEBUG:
            print(f"Initial bind failed: {e}")
            print("Trying alternative bind paths...")
        # If binding fails, try alternative bind paths
        for path in bind_paths[env]:
            try:
                if DEBUG:
                    print(f"Attempting to bind with path: {path.format(username=username)}")
                ad = domain.create_session_as_user(path.format(username=username), password)
                break
            except Exception as e:
                if DEBUG:
                    print(f"Bind with path {path.format(username=username)} failed: {e}")
                continue

    user1_data = get_user_data(user1_name, env, ad)
    user2_data = get_user_data(user2_name, env, ad)

    if DEBUG:
        print(f"User 1 data: {user1_data}")
        print(f"User 2 data: {user2_data}")

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
