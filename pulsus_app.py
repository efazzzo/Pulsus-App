import streamlit as st
import csv
from datetime import datetime

# === Load weather CSV (Charlotte only) ===
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

# === Logic for weather penalty ===
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

# === Metric templates ===
real_estate_subtypes = ["Apartment", "Single-Family", "Condo", "Townhouse", "Mobile Home"]
metric_templates = {
    "Real Estate": [
        {"label": "Year Built", "type": "age_decay", "max_years": 100, "weight": 0.2, "category": "Structure"},
        {"label": "Roof Age (years)", "type": "age_decay", "max_years": 25, "weight": 0.2, "category": "Structure"},
        {"label": "HVAC Last Serviced (e.g. May 18, 2025)", "type": "time_since_service", "max_months": 12, "weight": 0.3, "category": "Systems"},
        {"label": "Square Feet", "type": "range_fit", "ideal_range": [500, 2500], "weight": 0.3, "category": "Usability"}
    ],
    "Car": [
        {"label": "Year", "type": "age_decay", "max_years": 20, "weight": 0.25, "category": "Age"},
        {"label": "Mileage", "type": "mileage_decay", "max_miles": 200000, "weight": 0.3, "category": "Engine Health"},
        {"label": "Last Oil Change (e.g. May 18, 2025)", "type": "time_since_service", "max_months": 6, "weight": 0.25, "category": "Engine Health"},
        {"label": "Tire Condition (good/fair/poor)", "type": "exact_match", "ideal": "good", "weight": 0.2, "category": "Wear & Tear"}
    ]
}

# === Metric scoring logic ===
def evaluate_metric(metric, value):
    try:
        if metric["type"] == "age_decay":
            age = datetime.now().year - int(value)
            return max(0, 100 - (age / metric["max_years"]) * 100)
        elif metric["type"] == "time_since_service":
            last_date = datetime.strptime(value, "%B %d, %Y")
            months = (datetime.today().year - last_date.year) * 12 + (datetime.today().month - last_date.month)
            return max(0, 100 - (months / metric["max_months"]) * 100)
        elif metric["type"] == "range_fit":
            value = float(value)
            min_val, max_val = metric["ideal_range"]
            if min_val <= value <= max_val:
                return 100
            deviation = min(abs(value - min_val), abs(value - max_val))
            return max(0, 100 - (deviation / (max_val - min_val)) * 100)
        elif metric["type"] == "mileage_decay":
            value = float(value)
            return max(0, 100 - (value / metric["max_miles"]) * 100)
        elif metric["type"] == "exact_match":
            return 100 if value.lower() == metric["ideal"].lower() else 40
    except:
        return 0
    return 50

# === Streamlit UI ===
st.title("PULSUS Score – Charlotte, NC")
asset_type = st.selectbox("Choose Asset Type", ["Real Estate", "Car"])
subtype = None

if asset_type == "Real Estate":
    subtype = st.selectbox("Property Subtype", real_estate_subtypes)

st.subheader("Enter Asset Info")
inputs = {}
for metric in metric_templates[asset_type]:
    inputs[metric["label"]] = st.text_input(metric["label"])

if st.button("Calculate Score"):
    total_score = 0
    total_weight = 0
    category_scores = {}
    first_date = None

    for metric in metric_templates[asset_type]:
        value = inputs[metric["label"]].strip()
        if not value:
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

        if "Serviced" in metric["label"] or "Oil Change" in metric["label"]:
            first_date = value

    base_score = round(total_score / total_weight, 2)
    penalty = get_penalty_from_csv(first_date) if first_date else 0
    final_score = max(0, round(base_score - penalty, 2))

    st.success(f"Final Score: {final_score}%")
    st.write(f"Base Score: {base_score}%")
    st.write(f"Weather Penalty: -{penalty}%")

    st.subheader("Subcategory Breakdown")
    for cat, val in category_scores.items():
        cat_score = round(val["score"] / val["weight"], 2)
        st.write(f"- {cat}: {cat_score}%")
