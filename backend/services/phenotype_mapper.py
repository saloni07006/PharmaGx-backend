# ==========================================
# Phenotype Mapping Service
# ==========================================

def determine_phenotype(gene, diplotype):

    if gene == "CYP2D6":
        if "*4/*4" in diplotype:
            return "PM"
        if "*4" in diplotype:
            return "IM"
        if "*2" in diplotype:
            return "RM"
        return "NM"

    if gene == "CYP2C19":
        if "*2/*2" in diplotype:
            return "PM"
        if "*2" in diplotype:
            return "IM"
        if "*17" in diplotype:
            return "RM"
        return "NM"

    if gene == "CYP2C9":
        if "*3/*3" in diplotype:
            return "PM"
        if "*2" in diplotype or "*3" in diplotype:
            return "IM"
        return "NM"

    if gene in ["SLCO1B1", "TPMT", "DPYD"]:
        if "*2" in diplotype or "*3" in diplotype or "*5" in diplotype:
            return "IM"
        return "NM"

    return "Unknown"
