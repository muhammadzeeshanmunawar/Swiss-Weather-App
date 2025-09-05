import requests
from tkinter import *
from PIL import Image, ImageTk
import ttkbootstrap as tb
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import defaultdict

# ----------------------------
# CONFIG
# ----------------------------
API_KEY = "b54492035e17f4f582d3b94d7261816b"  # Replace with your API key
BASE_URL_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"

SWISS_CITIES = {
    "Zurich": {"lat": 47.3769, "lon": 8.5417},
    "Bern": {"lat": 46.9481, "lon": 7.4474},
    "Geneva": {"lat": 46.2044, "lon": 6.1432},
    "Basel": {"lat": 47.5596, "lon": 7.5886},
    "Lausanne": {"lat": 46.5197, "lon": 6.6323},
    "Lugano": {"lat": 46.0037, "lon": 8.9511},
    "St. Gallen": {"lat": 47.4245, "lon": 9.3767}
}

# ----------------------------
# ROOT WINDOW
# ----------------------------
root = tb.Window(themename="superhero")
root.geometry("480x750")
root.title("🇨🇭 Switzerland Weather App")
root.resizable(False, False)

# Background
bg_label = Label(root, bg="lightblue")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def get_current_weather(city):
    try:
        params = {"q": city + ",CH", "appid": API_KEY, "units": "metric"}
        data = requests.get(BASE_URL_CURRENT, params=params).json()
        if data.get("cod") != 200:
            weather_label.config(text="City not found!")
            weather_icon_label.config(image="")
            return None
        return data
    except:
        return None

def get_forecast(city):
    try:
        params = {"q": city + ",CH", "appid": API_KEY, "units": "metric"}
        data = requests.get(BASE_URL_FORECAST, params=params).json()
        if data.get("cod") != "200":
            return None
        return data
    except:
        return None

def update_weather():
    city = city_var.get()
    current = get_current_weather(city)
    if not current:
        weather_label.config(text="Error fetching weather")
        return

    temp = current["main"]["temp"]
    desc = current["weather"][0]["description"].title()
    icon_code = current["weather"][0]["icon"]

    weather_label.config(text=f"{city} Weather\n{temp}°C | {desc}")

    # Weather icon
    try:
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_img = Image.open(requests.get(icon_url, stream=True).raw)
        icon_img = icon_img.resize((100,100), Image.ANTIALIAS)
        icon_tk = ImageTk.PhotoImage(icon_img)
        weather_icon_label.config(image=icon_tk)
        weather_icon_label.image = icon_tk
    except:
        weather_icon_label.config(image="")

    # Forecast using free 5-day API
    forecast_data = get_forecast(city)
    if forecast_data and "list" in forecast_data:
        # Aggregate daily min/max
        daily_data = defaultdict(lambda: {"min": float("inf"), "max": float("-inf"), "icon": ""})
        for entry in forecast_data["list"]:
            dt_txt = entry["dt_txt"]
            dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            day_str = dt.strftime("%a")
            temp_min = entry["main"]["temp_min"]
            temp_max = entry["main"]["temp_max"]
            daily_data[day_str]["min"] = min(daily_data[day_str]["min"], temp_min)
            daily_data[day_str]["max"] = max(daily_data[day_str]["max"], temp_max)
            if not daily_data[day_str]["icon"]:
                daily_data[day_str]["icon"] = entry["weather"][0]["icon"]

        # Sort days by date
        ordered_days = list(daily_data.keys())
        if len(ordered_days) < 7:
            # Simulate remaining days by repeating last days
            while len(ordered_days) < 7:
                ordered_days.append(ordered_days[-1])
        
        # Forecast cards
        for widget in forecast_frame.winfo_children():
            widget.destroy()

        days_list, temps_max, temps_min = [], [], []
        for day_str in ordered_days[:7]:
            values = daily_data[day_str]
            day_max = int(values["max"])
            day_min = int(values["min"])
            icon_code = values["icon"]

            try:
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
                icon_img = Image.open(requests.get(icon_url, stream=True).raw)
                icon_img = icon_img.resize((50,50), Image.ANTIALIAS)
                icon_tk = ImageTk.PhotoImage(icon_img)
            except:
                icon_tk = None

            card = tb.Frame(forecast_frame, bootstyle="secondary", padding=5)
            card.pack(side=LEFT, padx=5)
            tb.Label(card, text=day_str, font=("Helvetica",10,"bold")).pack()
            if icon_tk:
                lbl_icon = tb.Label(card, image=icon_tk)
                lbl_icon.image = icon_tk
                lbl_icon.pack()
            tb.Label(card, text=f"{day_max}°C / {day_min}°C", font=("Helvetica",9)).pack()

            days_list.append(day_str)
            temps_max.append(day_max)
            temps_min.append(day_min)

        # Plot temperature graph
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(days_list, temps_max, marker='o', label="Max Temp", color='orange')
        ax.plot(days_list, temps_min, marker='o', label="Min Temp", color='blue')
        ax.set_title("7-Day Temperature Forecast (Simulated)")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        ax.grid(True)
        canvas.draw()
    else:
        # Forecast not available
        for widget in forecast_frame.winfo_children():
            widget.destroy()
        tb.Label(forecast_frame, text="7-Day Forecast not available", font=("Helvetica",12)).pack()

# ----------------------------
# GUI ELEMENTS
# ----------------------------
# Header
tb.Label(root, text="🌤️ Switzerland Weather", font=("Helvetica", 18, "bold")).pack(pady=10)
tb.Label(root, text="Developed by Zeeshan Munawar | University of Bern", font=("Helvetica", 10, "italic")).pack(pady=5)

# City dropdown
city_var = StringVar(value="Zurich")
tb.Combobox(root, values=list(SWISS_CITIES.keys()), textvariable=city_var, font=("Helvetica",12)).pack(pady=10)

# Get Weather button
tb.Button(root, text="Get Weather", bootstyle="info-outline", command=update_weather).pack(pady=10)

# Current weather
weather_icon_label = tb.Label(root)
weather_icon_label.pack()
weather_label = tb.Label(root, text="", font=("Helvetica",12))
weather_label.pack(pady=5)

# Forecast frame
forecast_frame = tb.Frame(root)
forecast_frame.pack(pady=10)

# Temperature graph
fig = plt.Figure(figsize=(5,2.5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

# Footer
tb.Label(root, text="© Zeeshan | Unibe Student", font=("Helvetica", 10, "italic")).pack(side=BOTTOM, pady=5)

# Default weather
update_weather()

root.mainloop()
