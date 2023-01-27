import customtkinter as tk
from tkinter import messagebox
from scrape import Scraper
from datetime import datetime 

tk.set_default_color_theme("green")
tk.set_appearance_mode("dark")
class App(tk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x300")
        self.title("Cheap ticket finder")

        self.frame = tk.CTkFrame(master=self)
        self.frame.pack(padx=20,pady=20,fill="both",expand=True)
        self.frame.grid_columnconfigure(1, weight=1)

        self.flight_type = tk.StringVar()
        self.flight_type.set("One Way")
        self.flight_type_menu = tk.CTkOptionMenu(master=self.frame,
                                        values=["One Way",'Round Trip'], variable=self.flight_type)
        self.flight_type_menu.grid(row=0,column=0,padx=20,pady=(20,10),sticky="e")

        self.seat_type = tk.CTkOptionMenu(master=self.frame,
                                        values=['Economy','Business','First class'])
        self.seat_type.grid(row=0,column=1,padx=30,pady=(20,10),sticky="w")

        self.confirm_button = tk.CTkButton(master=self.frame, text="Confirm", command=self.confirm)
        self.confirm_button.grid(row=0,column=2,padx=20,pady=(20,10))

    def confirm(self):
        self.dest_depart_label = tk.CTkLabel(master=self.frame, text="Airports (ex: YVR, SGN,...)")
        self.dest_depart_label.grid(row=1, column=0)
        self.dest = tk.CTkEntry(master=self.frame,
                            placeholder_text="To Where?")
        self.dest.grid(row=1,column=1,padx=10,pady=20)

        self.origin = tk.CTkEntry(master=self.frame,    
                            placeholder_text="From Where?")
        self.origin.grid(row=1,column=2,padx=10,pady=20)

        self.leave_return_label = tk.CTkLabel(master=self.frame, text="Leave-Return (MM-DD-YYYY)")
        self.leave_return_label.grid(row=2, column=0)

        self.date_leave = tk.CTkEntry(master=self.frame,
                            placeholder_text="MM-DD-YYYY",)
        self.date_leave.grid(row=2,column=1, padx=10,pady=20)
        today_date = datetime.today().strftime('%m-%d-%Y')
        self.date_leave.insert(0,today_date)
        
        self.date_return = tk.CTkEntry(master=self.frame,
                            placeholder_text="MM-DD-YYYY", state=["disabled" if self.flight_type_menu.get()=="One Way" else "normal"])
        self.date_return.grid(row=2,column=2, padx=10,pady=20) 

        self.find_button = tk.CTkButton(master=self.frame, command=self.find, text="Find")
        self.find_button.grid(row=3,column=1)
    
    def find(self):
        try:
            flight = Scraper(type=self.flight_type_menu.get(),
                                dest=self.dest.get(),
                                depart=self.origin.get(),
                                date_leave=self.date_leave.get(),
                                date_return=self.date_return.get(),
                                seat_class=self.seat_type.get())
        except Exception:
            messagebox.showerror("Loading error", "Error: There might be an issue with the site or internet connection" +
                                                    ". Please try again.")
        try:
            datetime.strptime(self.date_leave.get(), '%m-%d-%Y')
            if (self.date_leave.get()):
                datetime.strptime(self.date_return.get(), '%m-%d-%Y')
        except ValueError:
            messagebox.showerror("Day format error", "Error: you entered the wrong date format, please enter again")
        if self.flight_type_menu.get() == "One Way":
            flight.showOneWay()
        else:
            flight.showRoundTrip()
            
if __name__ == "__main__":
    app = App()
    app.mainloop()