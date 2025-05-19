import streamlit as st
import csv
from datetime import datetime

st.markdown(
    "<div style='text-align: center; margin-bottom: 10px;'>"
    "<img src='https://raw.githubusercontent.com/efazzzo/Pulsus-App/main/pulsus_logo.jpg' width='220'>"
    "</div>",
    unsafe_allow_html=True
)


# === City selection and weather file mapping ===
city = st.selectbox("Select a City", ["Charlotte, NC", "Houston, TX", "Orlando, FL"])
weather_files = {
    "Charlotte, NC": "charlotte_weather.csv",
    "Houston, TX": "houston_weather.csv",
    "Orlando, FL": "orlando_weather.csv"
}
selected_weather_file = weather_files[city]

@st.cache_data
def load_weather_data(file_path):
    weather = {}
    with open(file_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row['datetime'].strip()
            weather[date] = {
                'tempmax': float(row['tempmax']),
                'humidity': float(row['humidity']),
                'precip': float(row['precip'])
            }
    return weather
    weather_data = load_weather_data(selected_weather_file)

    weather = {}
    with open(file_path, newline='') as f:
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

metric_templates["Real Estate"] += [
    {
        "label": "Last General Inspection (e.g. May 2024)",
        "type": "time_since_service",
        "weight": 0.4,
        "category": "Maintenance & Service History",
        "max_months": 12
    },
    {
        "label": "Maintenance Frequency (monthly/annually/never)",
        "type": "frequency_match",
        "weight": 0.3,
        "category": "Maintenance & Service History",
        "ideal": "annually"
    },
    {
        "label": "Maintenance Log Available (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Maintenance & Service History",
        "ideal": "yes"
    },
    {
        "label": "Fire Extinguisher Present (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Fire & Life Safety",
        "ideal": "yes"
    },
    {
        "label": "Smoke Detector Last Tested (e.g. March 2025)",
        "type": "time_since_service",
        "weight": 0.4,
        "category": "Fire & Life Safety",
        "max_months": 6
    },
    {
        "label": "Emergency Exit Plan Posted (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Fire & Life Safety",
        "ideal": "yes"
    },
    {
        "label": "Solar Panels Installed (yes/no)",
        "type": "exact_match",
        "weight": 0.4,
        "category": "Environmental Impact",
        "ideal": "yes"
    },
    {
        "label": "Water-Efficient Appliances Present (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Environmental Impact",
        "ideal": "yes"
    },
    {
        "label": "EnergyStar or LEED Certified (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Environmental Impact",
        "ideal": "yes"
    },
    {
        "label": "Foundation Cracks Present (yes/no)",
        "type": "exact_match",
        "weight": 0.4,
        "category": "Foundation & Ground Risk",
        "ideal": "no"
    },
    {
        "label": "Recent Water Intrusion or Flooding (yes/no)",
        "type": "exact_match",
        "weight": 0.4,
        "category": "Foundation & Ground Risk",
        "ideal": "no"
    },
    {
        "label": "Sinkhole or Seismic Risk Zone (yes/no)",
        "type": "exact_match",
        "weight": 0.2,
        "category": "Foundation & Ground Risk",
        "ideal": "no"
    },
    {
        "label": "Smart Devices Installed (yes/no)",
        "type": "exact_match",
        "weight": 0.4,
        "category": "Connectivity & Smart Tech",
        "ideal": "yes"
    },
    {
        "label": "Wired for High-Speed Internet (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Connectivity & Smart Tech",
        "ideal": "yes"
    },
    {
        "label": "Cellular Signal Strength (poor/fair/good)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Connectivity & Smart Tech",
        "ideal": "good"
    },
    {
        "label": "Crime Level (low/medium/high)",
        "type": "exact_match",
        "weight": 0.4,
        "category": "Neighborhood & External Factors",
        "ideal": "low"
    },
    {
        "label": "Walkability Score (1-100)",
        "type": "range_fit",
        "weight": 0.3,
        "category": "Neighborhood & External Factors",
        "ideal_range": [60, 100]
    },
    {
        "label": "Near Major Road or Highway (yes/no)",
        "type": "exact_match",
        "weight": 0.3,
        "category": "Neighborhood & External Factors",
        "ideal": "no"
    },
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



    if category == "Systems":
        if score >= 80:
            return "HVAC and systems appear well-maintained. Maintain regular service schedule."
        elif score >= 60:
            return "Service overdue or irregular. Schedule maintenance for HVAC, plumbing, and electrical systems."
        else:
            return "Poor system upkeep. Immediate HVAC/electrical servicing recommended."

    if category == "Usability":
        if score >= 80:
            return "Usable and practical space configuration."
        elif score >= 60:
            return "Consider space efficiency upgrades or layout optimizations."
        else:
            return "Usability is limited. Renovation or layout redesign may improve function."

    if category == "Safety & Compliance":
        if score >= 80:
            return "Safety features are in place. Continue monthly testing."
        elif score >= 60:
            return "Some safety compliance gaps. Verify smoke detectors and safety signage."
        else:
            return "Critical safety concerns. Install or replace detectors and review compliance."

    if category == "Energy & Efficiency":
        if score >= 80:
            return "Windows and insulation performing well."
        elif score >= 60:
            return "Some inefficiencies present. Consider sealing gaps or replacing older windows."
        else:
            return "Poor energy efficiency. Window upgrades and insulation check recommended."

    if category == "Exposure":
        if score >= 80:
            return "Property exposure risk is low based on input."
        elif score >= 60:
            return "Moderate risk of environmental exposure (e.g., flood zone). Review mitigation options."
        else:
            return "High exposure risk noted. Flood protection or insurance review advised."

    return "No recommendation available."


def get_recommendation(category, score):
    if category == "Structure":
        if score >= 80:
            return "Roof and structure appear sound. Schedule a structural inspection every 5 years."
        elif score >= 60:
            return "Some aging or wear present. Schedule a roof inspection within the next year."
        else:
            return "High wear risk. Prioritize roofing repair and full inspection immediately."

    if category == "Systems":
        if score >= 80:
            return "Systems appear well-maintained. HVAC and plumbing should be serviced annually."
        elif score >= 60:
            return "Service overdue. Schedule HVAC and plumbing checks within 3 months."
        else:
            return "System condition is poor. Arrange immediate servicing and diagnostic testing."

    if category == "Usability":
        if score >= 80:
            return "Usable and practical layout. Reassess functionality every 3–5 years or before remodeling."
        elif score >= 60:
            return "Some limitations in usability. Consider renovations within 2 years."
        else:
            return "Major usability concerns. Renovation or layout redesign recommended in the next 6–12 months."

    if category == "Safety & Compliance":
        if score >= 80:
            return "Safety features active. Test smoke/carbon monoxide detectors monthly."
        elif score >= 60:
            return "Safety gaps noted. Ensure detector functionality and conduct a full safety audit within 3 months."
        else:
            return "Critical safety concerns. Address immediately by installing or replacing safety devices."

    if category == "Energy & Efficiency":
        if score >= 80:
            return "Energy efficiency is strong. Conduct insulation and window checks every 3–5 years."
        elif score >= 60:
            return "Moderate inefficiencies. Evaluate energy audit or upgrades within 1 year."
        else:
            return "Significant efficiency issues. Replace windows or insulation and conduct an energy audit ASAP."

    if category == "Exposure":
        if score >= 80:
            return "Exposure risks are minimal. Review flood zone status during annual property assessments."
        elif score >= 60:
            return "Moderate exposure. Consult local insurance and mitigation options within 6 months."
        else:
            return "High risk exposure. Install mitigation features and revise insurance within 3 months."

    return "No recommendation available."

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

        st.subheader("🔍 Detailed Subcategory Insights")
        for cat, val in category_scores.items():
            cat_score = round(val["score"] / val["weight"], 2)
            emoji = "✅" if cat_score >= 80 else ("⚠️" if cat_score >= 60 else "🚨")
            recommendation = get_recommendation(cat, cat_score)
            st.markdown(f"**{emoji} {cat} – {cat_score}%**")
            st.markdown(f"*Recommendation:* {recommendation}")
            st.markdown("---")
    
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