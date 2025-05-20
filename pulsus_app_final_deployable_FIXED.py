
import streamlit as st
import csv
from datetime import datetime
import os

# Logo
st.markdown(
    "<div style='text-align: center; margin-bottom: 10px;'>"
    "<img src='https://raw.githubusercontent.com/efazzzo/Pulsus-App/main/pulsus_logo.jpg' width='220'>"
    "</div>",
    unsafe_allow_html=True
)

# City selector
city = st.selectbox("Choose Your City", ["Charlotte", "Houston", "Orlando"])

# Mapping city to CSV file
weather_files = {
    "Charlotte": "charlotte_weather.csv",
    "Houston": "houston_weather.csv",
    "Orlando": "orlando_weather.csv"
}
selected_weather_file = weather_files.get(city, "")

@st.cache_data
def load_weather_data(filename):
    weather = {}
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_key = row["datetime"].strip()
            weather[date_key] = {
                "tempmax": float(row["tempmax"]),
                "humidity": float(row["humidity"]),
                "precip": float(row["precip"])
            }
    return weather

weather_data = load_weather_data(selected_weather_file)

st.write("✅ Weather data loaded successfully for", city)
