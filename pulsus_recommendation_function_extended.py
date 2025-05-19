
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
