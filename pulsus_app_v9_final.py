from datetime import datetime
import streamlit as st
import csv
weather_data = load_weather_data(selected_weather_file)
time import datetime

st.markdown(
    "<div style='text-align: center; margin-bottom: 10px;'>"
    "<img src='https://raw.githubusercontent.com/efazzzo/Pulsus-App/main/pulsus_logo.jpg' width='220'>"
    "</div>",
    unsafe_allow_html=True
)

@st.cache_data
def load_weather_data(file_path):
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

real_estate_subtypes = ["Apartment", "Single-Family", "Condo", "Townhouse", "Mobile Home"]
metric_templates = {
    "Real Estate": [
        {"label": "Year Built", "type": "age_decay", "max_years": 100, "weight": 0.15, "category": "Structure"},
        {"label": "Roof Age (years)", "type": "age_decay", "max_years": 25, "weight": 0.15, "category": "Structure"},
        {"label": "HVAC Last Serviced (e.g. May 18, 2025)", "type": "time_since_service", "max_months": 12, "weight": 0.2, "category": "Systems"},
        {"label": "Square Feet", "type": "range_fit", "ideal_range": [500, 2500], "weight": 0.15, "category": "Usability"},
        {"label": "Smoke Detectors Installed (yes/no)", "type": "exact_match", "ideal": "yes", "weight": 0.1, "category": "Safety & Compliance"},
        {"label": "Window Age (years)", "type": "age_decay", "max_years": 30, "weight": 0.1, "category": "Energy & Efficiency"},
        {"label": "Flood Zone (yes/no)", "type": "exact_match", "ideal": "no", "weight": 0.15, "category": "Exposure"}
    ]
}

def evaluate_metric(metric, value):
    try:
        if metric["type"] == "age_decay":
            age = datetime.now().year - int(value) if "Year" in metric["label"] else int(value)
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
        elif metric["type"] == "exact_match":
            return 100 if value.strip().lower() == metric["ideal"].lower() else 40
    except:
        return 0
    return 50

st.title("PULSUS Score – Property Diagnostic Tool")
asset_type = st.selectbox("Choose Asset Type", ["Real Estate", "Car"])
subtype = st.selectbox("Property Subtype", real_estate_subtypes) if asset_type == "Real Estate" else None
zip_code = st.text_input("Enter ZIP Code for Local Results", "28202")
parcel_number = st.text_input("Parcel Number (optional)")

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

    if parcel_number:
        lookup_url = get_parcel_lookup_url(parcel_number, zip_code)
        if lookup_url:
            st.markdown("---")
            st.markdown(f"📍 [View Parcel Info (Mecklenburg County)]({lookup_url})")