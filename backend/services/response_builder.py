# ==========================================
# Final JSON Response Builder
# ==========================================

from datetime import datetime
from services.llm_service import generate_explanation


def build_final_response(
    drug,
    primary_gene,
    diplotype,
    phenotype,
    variants,
    rule_risk,
    severity,
    confidence,
    annotation_warnings=None
):
    """
    Build hackathon-required structured JSON output.
    """

    response = {
        "patient_id": f"PATIENT_{datetime.utcnow().strftime('%H%M%S')}",
        "drug": drug,
        "timestamp": datetime.utcnow().isoformat(),

        # -----------------------------
        # Risk Assessment Section
        # -----------------------------
        "risk_assessment": {
            "risk_label": rule_risk,
            "confidence_score": confidence,
            "severity": severity
        },

        # -----------------------------
        # Pharmacogenomic Profile
        # -----------------------------
        "pharmacogenomic_profile": {
            "primary_gene": primary_gene,
            "diplotype": diplotype,
            "phenotype": phenotype,
            "detected_variants": variants
        },

        # -----------------------------
        # Clinical Recommendation
        # -----------------------------
        "clinical_recommendation": {
            "recommendation_summary": generate_recommendation(drug, rule_risk),
            "cpic_guideline_reference": f"CPIC Guideline for {primary_gene} and {drug}",
            "recommended_action": generate_action(rule_risk)
        },

        # -----------------------------
        # LLM Explanation
        # -----------------------------
        "llm_generated_explanation": {},

        # -----------------------------
        # Quality Metrics
        # -----------------------------
        "quality_metrics": {
            "vcf_parsing_success": True,
            "variants_detected": len(variants),
            "genes_matched": len(set(v["gene"] for v in variants)),
            "drugs_processed": 1,
            "annotation_warnings": annotation_warnings or []
        }
    }

    response["llm_generated_explanation"] = generate_explanation(response)

    return response


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def generate_recommendation(drug, risk):
    if risk == "Safe":
        return f"{drug} can be prescribed at standard dosage."
    if risk == "Adjust Dosage":
        return f"{drug} requires dosage adjustment."
    if risk == "Toxic":
        return f"Avoid {drug} due to high toxicity risk."
    if risk == "Ineffective":
        return f"{drug} may be ineffective due to metabolic variation."
    return "Consult specialist."


def generate_action(risk):
    if risk == "Safe":
        return "Proceed with standard treatment."
    if risk == "Adjust Dosage":
        return "Reduce or adjust dosage."
    if risk == "Toxic":
        return "Avoid drug and use alternative."
    if risk == "Ineffective":
        return "Consider alternative therapy."
    return "Further evaluation required."
