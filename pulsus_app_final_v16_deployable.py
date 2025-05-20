
import streamlit as st
import csv
from datetime import datetime
import os

# Logo and title
st.markdown(
    "<div style='text-align: center; margin-bottom: 10px;'>"
    "<img src='https://raw.githubusercontent.com/efazzzo/Pulsus-App/main/pulsus_logo.jpg' width='220'>"
    "</div>",
    unsafe_allow_html=True
)

st.title("PULSUS Score – Property Diagnostic Tool")

# City selection
city = st.selectbox("Choose Your City", ["Charlotte", "Houston", "Orlando"])
weather_files = {
    "Charlotte": "Charlotte_weather.csv",
    "Houston": "Houston_weather.csv",
    "Orlando": "Orlando_weather.csv"
}
selected_weather_file = weather_files[city]

# Load weather data
@st.cache_data
def load_weather_data(filename):
    weather = {}
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["datetime"].strip()
            weather[date] = {
                "tempmax": float(row["tempmax"]),
                "humidity": float(row["humidity"]),
                "precip": float(row["precip"])
            }
    return weather

weather_data = load_weather_data(selected_weather_file)

def get_penalty_from_csv(date_str):
    try:
        lookup_date = date_str.strftime("%Y-%m-%d")
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

real_estate_subtypes = ["Apartment", "Single-Family", "Condo", "Townhouse", "Mobile Home"]
metric_templates = [
    {"label": "Year Built", "type": "age_decay", "max_years": 100, "weight": 0.15, "category": "Structure"},
    {"label": "Roof Age (years)", "type": "age_decay", "max_years": 25, "weight": 0.15, "category": "Structure"},
    {"label": "HVAC Last Serviced", "type": "time_since_service", "max_months": 12, "weight": 0.2, "category": "Systems"},
    {"label": "Square Feet", "type": "range_fit", "ideal_range": [500, 2500], "weight": 0.15, "category": "Usability"},
    {"label": "Smoke Detectors Installed (yes/no)", "type": "exact_match", "ideal": "yes", "weight": 0.1, "category": "Safety & Compliance"},
    {"label": "Window Age (years)", "type": "age_decay", "max_years": 30, "weight": 0.1, "category": "Energy & Efficiency"},
    {"label": "Flood Zone (yes/no)", "type": "exact_match", "ideal": "no", "weight": 0.15, "category": "Exposure"},
    {"label": "Fire Extinguisher Present (yes/no)", "type": "exact_match", "ideal": "yes", "weight": 0.1, "category": "Safety & Compliance"}
]

def evaluate_metric(metric, value):
    try:
        if metric["type"] == "age_decay":
            age = datetime.now().year - int(value) if "Year" in metric["label"] else int(value)
            return max(0, 100 - (age / metric["max_years"]) * 100)
        elif metric["type"] == "time_since_service":
            months = (datetime.today().year - value.year) * 12 + (datetime.today().month - value.month)
            return max(0, 100 - (months / metric["max_months"]) * 100)
        elif metric["type"] == "range_fit":
            value = float(value)
            min_val, max_val = metric["ideal_range"]
            if min_val <= value <= max_val:
                return 100
            deviation = min(abs(value - min_val), abs(value - max_val))
            return max(0, 100 - (deviation / (max_val - min_val)) * 100)
        elif metric["type"] == "exact_match":
            return 100 if value.strip().lower() == metric["ideal"].lower() else 40
    except:
        return 0
    return 50

# Form inputs
subtype = st.selectbox("Property Subtype", real_estate_subtypes)
zip_code = st.text_input("Enter ZIP Code for Local Results", "28202")

st.subheader("Enter Asset Info")
inputs = {}
for metric in metric_templates:
    if "Date" in metric["label"] or "Serviced" in metric["label"]:
        inputs[metric["label"]] = st.date_input(metric["label"])
    elif "yes/no" in metric["label"].lower():
        inputs[metric["label"]] = st.selectbox(metric["label"], ["yes", "no"])
    else:
        inputs[metric["label"]] = st.text_input(metric["label"])

if st.button("Calculate Score"):
    total_score = 0
    total_weight = 0
    category_scores = {}
    first_date = None

    for metric in metric_templates:
        value = inputs[metric["label"]]
        if value == "":
            st.warning(f"Please fill in: {metric['label']}")
            st.stop()
        score = evaluate_metric(metric, value)
        weight = metric["weight"]
        total_score += score * weight
        total_weight += weight

        category = metric["category"]
        if category not in category_scores:
            category_scores[category] = {"score": 0, "weight": 0}
        category_scores[category]["score"] += score * weight
        category_scores[category]["weight"] += weight

        if "Serviced" in metric["label"]:
            first_date = value

    base_score = round(total_score / total_weight, 2)
    penalty = get_penalty_from_csv(first_date) if first_date else 0
    final_score = max(0, round(base_score - penalty, 2))
    letter = get_letter_grade(final_score)

    st.markdown(f"<h1 style='text-align:center; font-size: 64px;'>Score: {final_score}% — Grade {letter}</h1>", unsafe_allow_html=True)
    st.progress(final_score / 100)

    if letter == "A":
        st.success("✅ Excellent Condition")
    elif letter == "B":
        st.info("👍 Good Shape")
    elif letter == "C":
        st.warning("⚠️ Fair – Needs Monitoring")
    elif letter == "D":
        st.warning("🔧 Needs Some Repairs")
    else:
        st.error("🚨 Poor Condition – Attention Required")

    st.write(f"Base Score: **{base_score}%**")
    st.write(f"Weather Penalty: **-{penalty}%**")

    st.subheader("📊 Subcategory Breakdown")
    for cat, val in category_scores.items():
        cat_score = round(val["score"] / val["weight"], 2)
        emoji = "✅" if cat_score >= 80 else ("⚠️" if cat_score >= 60 else "🚨")
        st.write(f"{emoji} **{cat}**: {cat_score}%")

    st.markdown("---")
    st.subheader(f"🔧 Local Technician Listings Near {zip_code}")
    st.markdown(f"- [HVAC Technicians]({format_yelp_link('HVAC', zip_code)})")
    st.markdown(f"- [Roofing Contractors]({format_yelp_link('Roofing', zip_code)})")
    st.markdown(f"- [Electricians]({format_yelp_link('Electricians', zip_code)})")
    st.markdown(f"- [Plumbers]({format_yelp_link('Plumbers', zip_code)})")
    st.markdown(f"- [Window Installers]({format_yelp_link('Window Installation', zip_code)})")
