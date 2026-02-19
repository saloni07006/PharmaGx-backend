# ==========================================
# CPIC Rule-Based Risk Engine
# ==========================================

def rule_based_risk(drug: str, phenotype: str):
    """
    Determine drug risk using CPIC-style deterministic rules.
    Returns: (risk_label, severity)
    """

    drug = drug.upper()
    phenotype = phenotype.upper()

    # ---------------------------------------
    # CODEINE - CYP2D6
    # ---------------------------------------
    if drug == "CODEINE":
        if phenotype == "PM":
            return "Ineffective", "moderate"
        if phenotype in ["RM", "URM"]:
            return "Toxic", "high"
        return "Safe", "none"

    # ---------------------------------------
    # WARFARIN - CYP2C9
    # ---------------------------------------
    if drug == "WARFARIN":
        if phenotype in ["PM", "IM"]:
            return "Adjust Dosage", "moderate"
        return "Safe", "none"

    # ---------------------------------------
    # CLOPIDOGREL - CYP2C19
    # ---------------------------------------
    if drug == "CLOPIDOGREL":
        if phenotype == "PM":
            return "Ineffective", "high"
        if phenotype == "IM":
            return "Adjust Dosage", "moderate"
        return "Safe", "none"

    # ---------------------------------------
    # SIMVASTATIN - SLCO1B1
    # ---------------------------------------
    if drug == "SIMVASTATIN":
        if phenotype == "IM":
            return "Adjust Dosage", "moderate"
        return "Safe", "none"

    # ---------------------------------------
    # AZATHIOPRINE - TPMT
    # ---------------------------------------
    if drug == "AZATHIOPRINE":
        if phenotype == "IM":
            return "Toxic", "high"
        return "Safe", "none"

    # ---------------------------------------
    # FLUOROURACIL - DPYD
    # ---------------------------------------
    if drug == "FLUOROURACIL":
        if phenotype == "IM":
            return "Toxic", "critical"
        return "Safe", "none"

    return "Unknown", "low"
