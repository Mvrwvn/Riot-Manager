import customtkinter as ctk
from customtkinter import filedialog
import json
from opgg.opgg import OPGG
from PIL import Image
import io
import requests
import tkinter as tk
from CTkToolTip import *
from tkinter import messagebox
from script import launch

class MainWindow:
    def __init__(self) -> None:
        self.root = ctk.CTk()
        self.root.geometry("700x400")
        self.root.title("Riot Manager")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        self.opgg_obj = OPGG()
        self.logo = ctk.CTkImage(dark_image=Image.open("resource/Riot_Manager_white.png"),size=(220, 100))
        self.label_logo = ctk.CTkLabel(self.root, text="", image=self.logo)
        self.label_logo.place(x=30, y=5)
        self.font = ctk.CTkFont(family="Helvetica", weight="bold", size=25)
        self.font2 = ctk.CTkFont(weight="bold", size=65)
        self.label = ctk.CTkLabel(self.root, text="Who's playing ?", font=self.font, text_color=("#E4102D", "#FFFFFF"))
        self.label.place(x=257 ,y=105)
        self.frame_profile = ctk.CTkFrame(self.root, width=700,height=91, fg_color="transparent")
        self.frame_profile.pack(anchor=ctk.CENTER, expand=True)
        self.load_profiles()

    def do_popup(self, event, index):
        with open("data/riot_manager.json", "r") as f:
            data = json.load(f)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Edit", command= lambda: self.edit_profile(data['Profiles'][index]))
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command= lambda: self.delete_profile(index))
        self.menu.add_separator()
        self.menu.add_command(label="Refresh", command=self.refresh_profiles)
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def add_profile(self):
        add_window = AddProfileWindow(self.root)
        self.root.wait_window(add_window.new_page)
        self.refresh_profiles()
        self.root.deiconify()

    def edit_profile(self, data):
        add_window = AddProfileWindow(self.root, data=data)
        self.root.wait_window(add_window.new_page)
        self.refresh_profiles()
        self.root.deiconify()

    def delete_profile(self, index):
        with open("data/riot_manager.json", "r") as f:
            data = json.load(f)
        data["Profiles"].pop(index)
        with open("data/riot_manager.json", "w") as f:
            json.dump(data, f, indent=4)
        self.refresh_profiles()

    def download_image(self, url):
        response = requests.get(url)
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))
        return ctk.CTkImage(image, size=(90, 90))

    def load_profiles(self):
        with open("data/riot_manager.json", "r") as f:
            data = json.load(f)
        for i in range(len(data["Profiles"])):
            self.opgg_obj.search(data["Profiles"][i]["riot_id"], data["Profiles"][i]["region"])
            if data["Options"]["mode"] == "tier_image_url":
                image_url = self.opgg_obj.get_summoner(True)['summoner']['league_stats'][0]['tier_info']['tier_image_url']
            elif data["Options"]["mode"] == "profile_image_url":
                image_url = self.opgg_obj.get_summoner(True)['summoner']['profile_image_url']
            image = self.download_image(image_url)
            self.login_button = ctk.CTkButton(self.frame_profile, image=image, text="", fg_color="transparent", 
                                               hover_color="#FFFFFF", width=85, height=85, 
                                               command= lambda index = i: launch(data['Profiles'][index]['username'], 
                                                                                 data['Profiles'][index]['password'], 
                                                                                 data['Options']['riot_client_path']))
            self.login_button.image = image
            self.login_button.bind("<Button-3>", command= lambda event, index = i: self.do_popup(event, index))
            self.login_button.pack(side=ctk.LEFT, padx=10)
            CTkToolTip(self.login_button,
                        message=f"{data['Profiles'][i]['riot_id']}\n"
                        f"{self.opgg_obj.get_summoner(True)['summoner']['league_stats'][0]['tier_info']['tier']} "
                        f"{self.opgg_obj.get_summoner(True)['summoner']['league_stats'][0]['tier_info']['division']}\n"
                        f"{self.opgg_obj.get_summoner(True)['summoner']['league_stats'][0]['tier_info']['lp']} LP"
                        )
        self.add_profile_button = ctk.CTkButton(self.frame_profile, text="+",  fg_color="transparent", hover_color="#E4102D", 
                                                font=self.font2, width=90, height=90, command=self.add_profile)
        self.add_profile_button.pack(side=ctk.RIGHT, padx=10)

    def refresh_profiles(self):
        for widget in self.frame_profile.winfo_children():
            widget.destroy()
        self.load_profiles()

class SettingsWindow:
    def __init__(self,root, button_settings) -> None:
        with open("data/riot_manager.json", "r") as f:
            self.data = json.load(f)
        self.mode = self.data["Options"]["mode"]
        self.root = root
        self.button_settings = button_settings
        self.button_settings.configure(state="disabled")
        self.new_page = ctk.CTkToplevel(self.root)
        self.new_page.geometry("700x400")
        self.new_page.title("Settings")
        self.new_page.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.label_change_riot_path = ctk.CTkLabel(self.new_page, text="Change Riot path", font=ctk.CTkFont(size=15, weight="bold"))
        self.label_change_riot_path.pack(side = ctk.LEFT, padx=10)
        self.label_current_riot_path = ctk.CTkLabel(self.new_page, text=f"Current Riot path: {self.data['Options']['riot_client_path']}", 
                                                    font=ctk.CTkFont(size=10))
        self.label_current_riot_path.pack(side = ctk.LEFT, padx=10)
        self.button_file_dialog = ctk.CTkButton(self.new_page, text="Open riot path", command=self.open_file_dialog)
        self.button_file_dialog.pack(side = ctk.RIGHT, padx=10)
        self.label_change_display_mode = ctk.CTkLabel(self.new_page, text="Change display mode", font=ctk.CTkFont(size=15, weight="bold"))
        self.label_change_display_mode.pack(side = ctk.LEFT, padx=10)
        self.variable = ctk.StringVar(value=self.mode)
        self.button_profile_icon = ctk.CTkRadioButton(self.new_page, text="Profile Icon", command=self.switch_event, value="Profile Icon")
        self.button_profile_icon.pack(side = ctk.LEFT, padx=10)
        self.button_rank_icon = ctk.CTkRadioButton(self.new_page, text="Rank Icon", command=self.switch_event, value="Rank Icon")
        self.button_rank_icon.pack(side = ctk.LEFT, padx=10)

    def switch_event(self):
        with open("data/riot_manager.json", "r") as f:
            data = json.load(f)
        if self.variable.get() == "Profile Icon":
            data["Options"]["mode"] = "profile_image_url"
        else:
            data["Options"]["mode"] = "tier_image_url"
        with open("data/riot_manager.json", "w") as f:
            json.dump(data, f, indent=4)


    def is_selected(self):
        with open("data/riot_manager.json", "r") as f:
            data = json.load(f)
        if data["Options"]["mode"] == "profile_image_url":
            self.switch.select()
        else:
            self.switch.deselect()

    def on_closing(self):
        self.new_page.destroy()
        self.root.deiconify()
        self.button_settings.configure(state="normal")

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(defaultextension=".exe", filetypes=[("Executable files", "*.exe")], 
                                               title="Select the Riot Client executable")
        with open("data/riot_manager.json", "r") as f:
            data = json.load(f)
        data["Options"]["riot_client_path"] = file_path
        with open("data/riot_manager.json", "w") as f:
            json.dump(data, f, indent=4)

class AddProfileWindow:
    def __init__(self, root, data = None) -> None:
        self.root = root
        self.data = data
        self.root.withdraw()
        self.new_page = ctk.CTkToplevel(self.root)
        self.new_page.geometry("700x400")
        self.new_page.title("Smurf Manager")
        self.new_page.resizable(False, False)
        self.main_frame = ctk.CTkFrame(self.new_page, width=400,height=350, fg_color="transparent")
        self.main_frame.place(x=300, y=30)
        self.font = ctk.CTkFont(size=15, weight="bold")
        self.font2 = ctk.CTkFont(size=65, weight="bold")
        self.logo = ctk.CTkImage(dark_image=Image.open("resource/Riot_Manager_white.png"),size=(220, 100))
        self.logo_label = ctk.CTkLabel(self.new_page, text="", image=self.logo)
        self.logo_label.place(x=55, y=3)
        self.close_button = ctk.CTkButton(self.new_page, text="<", command=self.on_closing, fg_color="transparent", 
                                          hover_color="#E4102D", font=self.font2, width=50, height=50)
        self.close_button.place(x=0, y=0)
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=300, height=35)
        self.username_entry.pack(pady=10)
        if self.data is not None:
            self.username_entry.insert(0, self.data["username"])
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", width=300, height=35)
        self.password_entry.pack(pady=10)
        if self.data is not None:
            self.password_entry.insert(0, self.data["password"])
        self.riot_id_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Riot ID#1234", width=300, height=35)
        self.riot_id_entry.pack(pady=10)
        if self.data is not None:
            self.riot_id_entry.insert(0, self.data["riot_id"])
        self.region_entry = ctk.CTkOptionMenu(self.main_frame,values=["EUW", "EUNE", "NA", "KR", "BR", "LAN", "LAS", "OCE", "RU", "TR"], 
                                              fg_color="#E4102D", button_color="#E4102D", button_hover_color="#E4102D", 
                                              width=300, height=35)
        self.region_entry.pack(pady=10)
        if self.data is not None:
            self.region_entry.set(self.data["region"])

        self.validate_button = ctk.CTkButton(self.main_frame, text="Save Account", font=self.font, fg_color="#E4102D", 
                                             hover_color="#E4102D", command=self.validate, width=300, height=50)
        self.validate_button.pack(pady=10)

    def on_closing(self):
        self.new_page.destroy()

    def validate(self):
        if self.data is None:
            try:
                self.opgg_obj = OPGG()
                self.opgg_obj.search(self.riot_id_entry.get(), self.region_entry.get())
                with open("data/riot_manager.json", "r") as f:
                    data = json.load(f)
                data["Profiles"].append({
                    "username": self.username_entry.get(),
                    "password": self.password_entry.get(),
                    "riot_id": self.riot_id_entry.get(),
                    "region": self.region_entry.get()
                })
                with open("data/riot_manager.json", "w") as f:
                    json.dump(data, f, indent=4)
                self.on_closing()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            with open("data/riot_manager.json", "r") as f:
                data = json.load(f)
            data["Profiles"].append({
                "username": self.username_entry.get(),
                "password": self.password_entry.get(),
                "riot_id": self.riot_id_entry.get(),
                "region": self.region_entry.get()
            })
            data["Profiles"].pop(data["Profiles"].index(self.data))
            with open("data/riot_manager.json", "w") as f:
                json.dump(data, f, indent=4)
            self.on_closing()


if __name__ == "__main__":
    app = MainWindow()
    app.root.mainloop()
