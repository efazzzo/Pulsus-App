import streamlit as st
import csv
from datetime import datetime
from datetime import date

# === Header with Logo ===
st.markdown(
    "<div style='text-align: center; margin-bottom: 10px;'>"
    "<img src='https://raw.githubusercontent.com/efazzzo/Pulsus-App/main/pulsus_logo.jpg' width='220'>"
    "</div>",
    unsafe_allow_html=True
)

# === Load weather data based on city ===
@st.cache_data
def load_weather_data(file_name):
    weather = {}
    with open(file_name, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_key = row["date"].strip()
            weather[date_key] = {
                "tempmax": float(row["temperature_2m_max (°F)"]),
                "humidity": float(row["relative_humidity_2m_max (%)"]),
                "precip": float(row["precipitation_sum (inch)"])
            }
    return weather

def get_penalty_from_csv(date_obj, weather_data):
    try:
        lookup_date = date_obj.strftime("%Y-%m-%d")
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

# === Main UI ===
st.title("PULSUS Score – Property Diagnostic Tool")

city_choice = st.selectbox("Choose Your City", ["Charlotte", "Houston", "Orlando"])
weather_file_map = {
    "Charlotte": "charlotte_weather.csv",
    "Houston": "houston_weather.csv",
    "Orlando": "orlando_weather.csv"
}
selected_weather_file = weather_file_map[city_choice]
weather_data = load_weather_data(selected_weather_file)

# Inputs
year_built = st.date_input("Year Built", value=date(2000, 1, 1))
roof_age = st.number_input("Roof Age (years)", min_value=0)
hvac_date = st.date_input("HVAC Last Serviced")
square_feet = st.number_input("Square Feet", min_value=100)
smoke_detectors = st.selectbox("Smoke Detectors Installed", ["Yes", "No"])
window_age = st.number_input("Window Age (years)", min_value=0)
flood_zone = st.selectbox("Flood Zone", ["Yes", "No"])
fire_extinguisher = st.selectbox("Fire Extinguisher Present", ["Yes", "No"])
zip_code = st.text_input("Zip Code", "28202")

if st.button("Calculate Score"):
    scores = []
    categories = {
        "Structure": [],
        "Systems": [],
        "Usability": [],
        "Safety & Compliance": [],
        "Energy & Efficiency": [],
        "Exposure": []
    }

    # Evaluation
    current_year = datetime.now().year
    structure_score = max(0, 100 - ((current_year - year_built.year) / 100) * 100)
    categories["Structure"].append((structure_score, 0.15))

    roof_score = max(0, 100 - (roof_age / 25) * 100)
    categories["Structure"].append((roof_score, 0.15))

    months_since_hvac = (datetime.now().year - hvac_date.year) * 12 + (datetime.now().month - hvac_date.month)
    hvac_score = max(0, 100 - (months_since_hvac / 12) * 100)
    categories["Systems"].append((hvac_score, 0.2))

    usability_score = 100 if 500 <= square_feet <= 2500 else max(0, 100 - abs(square_feet - 1500)/20)
    categories["Usability"].append((usability_score, 0.15))

    smoke_score = 100 if smoke_detectors.lower() == "yes" else 40
    categories["Safety & Compliance"].append((smoke_score, 0.1))

    window_score = max(0, 100 - (window_age / 30) * 100)
    categories["Energy & Efficiency"].append((window_score, 0.1))

    flood_score = 100 if flood_zone.lower() == "no" else 40
    categories["Exposure"].append((flood_score, 0.15))

    fire_score = 100 if fire_extinguisher.lower() == "yes" else 40
    categories["Safety & Compliance"].append((fire_score, 0.1))

    # Aggregate
    total_score = 0
    total_weight = 0
    sub_breakdown = {}
    for cat, metrics in categories.items():
        cat_score = sum(score * weight for score, weight in metrics)
        cat_weight = sum(weight for _, weight in metrics)
        final_cat = round(cat_score / cat_weight, 2) if cat_weight > 0 else 0
        sub_breakdown[cat] = final_cat
        total_score += cat_score
        total_weight += cat_weight

    base_score = round(total_score / total_weight, 2)
    penalty = get_penalty_from_csv(hvac_date, weather_data)
    final_score = max(0, round(base_score - penalty, 2))
    letter = get_letter_grade(final_score)

    # Display
    st.markdown(f"<h1 style='text-align:center; font-size: 64px;'>Score: {final_score}% — Grade {letter}</h1>", unsafe_allow_html=True)
    st.progress(final_score / 100)

    st.write(f"Base Score: **{base_score}%**")
    st.write(f"Weather Penalty: **-{penalty}%**")

    st.subheader("📊 Subcategory Breakdown")
    for cat, val in sub_breakdown.items():
        emoji = "✅" if val >= 80 else ("⚠️" if val >= 60 else "🚨")
        st.write(f"{emoji} **{cat}**: {val}%")

    st.subheader(f"🔧 Local Technician Listings Near {zip_code}")
    for svc in ["HVAC", "Roofing", "Electricians", "Plumbers", "Window Installation"]:
        st.markdown(f"- [{svc}]({format_yelp_link(svc, zip_code)})")
