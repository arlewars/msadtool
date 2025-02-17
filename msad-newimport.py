import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from ms_active_directory.core.ad_domain import ADDomain, Credentials
from ms_active_directory.core.ad_connection_settings import ADDomainConnectionSettings, SSLConfiguration

NORD_STYLES = {
    "standard": {
        "background": "#2C2C2E",
        "foreground": "#F2F2F7",
        "highlight": "#1E4BC3",
        "error": "#FF453A",
        "header": "#c1cfff",
        "row_odd": "#C7E0F4",
        "row_even": "#F2F7FB",
        "button": "#FFCA4F",
        "invert_button": "#5AC8FA",
        "button_background": "#0A84FF"
    },
    "frost": {
        "background": "#8FBCBB",
        "foreground": "#2E3440",
        "highlight": "#88C0D0",
        "error": "#BF616A",
        "header": "#81a1c1",
        "row_odd": "#A3BE8C",
        "row_even": "#EBCB8B",
        "button": "#5E81AC",
        "invert_button": "#D08770",
        "button_background": "#88c0d0"
    },
    "aurora": {
        "background": "#A3BE8C",
        "foreground": "#2E3440",
        "highlight": "#88C0D0",
        "error": "#BF616A",
        "header": "#b48ead",
        "row_odd": "#A3BE8C",
        "row_even": "#EBCB8B",
        "button": "#5E81AC",
        "invert_button": "#D08770",
        "button_background": "#ebcb8b"
    }
}

DEFAULT_THEME = NORD_STYLES["standard"]

class ADApp:
    def __init__(self, root, theme=DEFAULT_THEME):
        self.root = root
        self.theme = theme
        self.apply_theme()

        self.root.title("Active Directory Management")

        # Domain Selection
        self.domain_label = tk.Label(root, text="Select Domain:", bg=self.theme["background"], fg=self.theme["foreground"])
        self.domain_label.grid(row=0, column=0)
        self.domain_var = tk.StringVar()
        self.domain_combobox = ttk.Combobox(root, textvariable=self.domain_var)
        self.domain_combobox['values'] = ['prod.domain', 'qa.domain', 'dev.domain']
        self.domain_combobox.grid(row=0, column=1)

        # Login Credentials
        self.user_label = tk.Label(root, text="Username:", bg=self.theme["background"], fg=self.theme["foreground"])
        self.user_label.grid(row=1, column=0)
        self.user_entry = tk.Entry(root, bg=self.theme["background"], fg=self.theme["foreground"])
        self.user_entry.grid(row=1, column=1)

        self.pass_label = tk.Label(root, text="Password:", bg=self.theme["background"], fg=self.theme["foreground"])
        self.pass_label.grid(row=2, column=0)
        self.pass_entry = tk.Entry(root, show='*', bg=self.theme["background"], fg=self.theme["foreground"])
        self.pass_entry.grid(row=2, column=1)

        # User/Group Selection
        self.option_var = tk.StringVar()
        self.user_radio = tk.Radiobutton(root, text="User", variable=self.option_var, value="User", bg=self.theme["background"], fg=self.theme["foreground"])
        self.user_radio.grid(row=3, column=0)
        self.group_radio = tk.Radiobutton(root, text="Group", variable=self.option_var, value="Group", bg=self.theme["background"], fg=self.theme["foreground"])
        self.group_radio.grid(row=3, column=1)

        # Action Buttons
        self.query_button = tk.Button(root, text="Query", command=self.query_ad, bg=self.theme["button_background"], fg=self.theme["foreground"])
        self.query_button.grid(row=4, column=0)

        self.add_button = tk.Button(root, text="Add User", command=self.add_user, bg=self.theme["button_background"], fg=self.theme["foreground"])
        self.add_button.grid(row=4, column=1)

        self.compare_button = tk.Button(root, text="Compare", command=self.compare_users, bg=self.theme["button_background"], fg=self.theme["foreground"])
        self.compare_button.grid(row=5, column=0)

        self.export_button = tk.Button(root, text="Export", command=self.export_csv, bg=self.theme["button_background"], fg=self.theme["foreground"])
        self.export_button.grid(row=5, column=1)

        # Frames for results
        self.frame1 = tk.Frame(root, bg=self.theme["background"])
        self.frame1.grid(row=6, column=0, columnspan=2)

        self.frame2 = tk.Frame(root, bg=self.theme["background"])
        self.frame2.grid(row=7, column=0, columnspan=2)

        # Store queried users and groups
        self.users = []
        self.groups = []

    def apply_theme(self):
        self.root.configure(bg=self.theme["background"])

    def query_ad(self):
        domain = self.domain_var.get()
        username = self.user_entry.get()
        password = self.pass_entry.get()

        credentials = Credentials(username, password)
        connection_settings = ADDomainConnectionSettings(
            ssl_configuration=SSLConfiguration(trust_all_certificates=True),
            follow_referrals=True
        )
        ad_domain = ADDomain(domain, credentials, connection_settings=connection_settings)

        if self.option_var.get() == "User":
            user_name = tk.simpledialog.askstring("Query User", "Enter User Name:")
            user = ad_domain.get_user(user_name)
            self.display_user_info(user)
        elif self.option_var.get() == "Group":
            group_name = tk.simpledialog.askstring("Query Group", "Enter Group Name:")
            group = ad_domain.get_group(group_name)
            self.display_group_info(group)

    def display_user_info(self, user):
        self.users.append(user)
        info = f"User: {user.name}\nGroups: {', '.join(user.get_member_of_group_names())}"
        label = tk.Label(self.frame1, text=info, justify="left", bg=self.theme["background"], fg=self.theme["foreground"])
        label.pack()

    def display_group_info(self, group):
        self.groups.append(group)
        info = f"Group: {group.name}\nMembers: {', '.join(group.get_member_names())}"
        label = tk.Label(self.frame1, text=info, justify="left", bg=self.theme["background"], fg=self.theme["foreground"])
        label.pack()

    def add_user(self):
        user_name = tk.simpledialog.askstring("Add User", "Enter User Name:")
        domain = self.domain_var.get()
        username = self.user_entry.get()
        password = self.pass_entry.get()

        credentials = Credentials(username, password)
        connection_settings = ADDomainConnectionSettings(
            ssl_configuration=SSLConfiguration(trust_all_certificates=True),
            follow_referrals=True
        )
        ad_domain = ADDomain(domain, credentials, connection_settings=connection_settings)
        user = ad_domain.get_user(user_name)
        self.display_user_info(user)

    def compare_users(self):
        if len(self.users) < 2:
            messagebox.showerror("Error", "Please add at least two users to compare.")
            return

        user1, user2 = self.users[:2]
        groups1 = set(user1.get_member_of_group_names())
        groups2 = set(user2.get_member_of_group_names())

        only_in_user1 = groups1 - groups2
        only_in_user2 = groups2 - groups1

        info = f"Groups only in {user1.name}: {', '.join(only_in_user1)}\n"
        info += f"Groups only in {user2.name}: {', '.join(only_in_user2)}"

        label = tk.Label(self.frame2, text=info, justify="left", bg=self.theme["background"], fg=self.theme["foreground"])
        label.pack()

    def export_csv(self):
        if len(self.users) < 2:
            messagebox.showerror("Error", "Please add at least two users to export comparison.")
            return

        user1, user2 = self.users[:2]
        groups1 = set(user1.get_member_of_group_names())
        groups2 = set(user2.get_member_of_group_names())

        only_in_user1 = groups1 - groups2
        only_in_user2 = groups2 - groups1

        data = {
            f"Groups only in {user1.name}": list(only_in_user1),
            f"Groups only in {user2.name}": list(only_in_user2)
        }

        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
        df.to_csv("comparison.csv", index=False)

        messagebox.showinfo("Export", "Comparison exported to 'comparison.csv'")

if __name__ == "__main__":
    root = tk.Tk()
    theme = NORD_STYLES["standard"]  # Change to your desired theme, e.g., "frost" or "aurora"
    app = ADApp(root, theme)
    root.mainloop()
