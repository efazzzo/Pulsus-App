
import streamlit as st
import csv
from datetime import datetime

st.markdown(
    "<div style='text-align: center; margin-bottom: 10px;'>"
    "<img src='https://raw.githubusercontent.com/efazzzo/Pulsus-App/main/pulsus_logo.jpg' width='220'>"
    "</div>",
    unsafe_allow_html=True
)

@st.cache_data
def load_weather_data():
    weather = {}
    with open("Charlotte_weather.csv", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["datetime"].strip()
            weather[date] = {
                "tempmax": float(row["tempmax"]),
                "humidity": float(row["humidity"]),
                "precip": float(row["precip"])
            }
    return weather

weather_data = load_weather_data()

def get_penalty_from_csv(date_str):
    try:
        lookup_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        if lookup_date not in weather_data:
            return 0
        temp = weather_data[lookup_date]["tempmax"]
        humidity = weather_data[lookup_date]["humidity"]
        precip = weather_data[lookup_date]["precip"]
        heat_score = min(temp / 100, 1.0)
        humidity_score = min(humidity / 100, 1.0)
        rain_score = min(precip / 2.0, 1.0)
        return round((heat_score * 0.2 + humidity_score * 0.3 + rain_score * 0.2) * 10, 2)
    except:
        return 0

def get_letter_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def format_yelp_link(service, zip_code):
    return f"https://www.yelp.com/search?find_desc={service.replace(' ', '+')}&find_loc={zip_code}"

def get_parcel_lookup_url(parcel, zip_code):
    if parcel and zip_code.startswith("28"):
        return "https://property.spatialest.com/nc/mecklenburg/#/"
    return None

st.title("PULSUS Score – Property Diagnostic Tool")

asset_type = st.selectbox("Choose Asset Type", ["Real Estate", "Car"])
real_estate_subtypes = ["Apartment", "Single-Family", "Condo", "Townhouse", "Mobile Home"]
subtype = st.selectbox("Property Subtype", real_estate_subtypes) if asset_type == "Real Estate" else None
zip_code = st.text_input("Enter ZIP Code for Local Results", "28202")
parcel_number = st.text_input("Parcel Number (optional)")

st.subheader("Enter Asset Info")
st.write("Inputs and further logic would go here...")
