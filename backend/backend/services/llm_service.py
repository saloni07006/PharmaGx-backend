import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


def _load_env_file() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    env_path = backend_root / ".env"
    load_dotenv(dotenv_path=env_path)


def _get_client() -> Groq:
    _load_env_file()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


def generate_explanation(risk_result: dict) -> dict:
    gene = risk_result.get("pharmacogenomic_profile", {}).get("primary_gene", "Unknown")
    drug = risk_result.get("drug", "Unknown")
    label = risk_result.get("risk_assessment", {}).get("risk_label", "Unknown")

    prompt = f"""
    Explain the pharmacogenomic interaction briefly.

    Gene: {gene}
    Drug: {drug}
    Risk: {label}

    Respond in EXACTLY 3 short lines:
    1. Clinical summary (max 15 words)
    2. Biological mechanism (max 12 words)
    3. Patient-friendly note (max 12 words)

    Do NOT include numbering, paragraphs, or extra text.
    """

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        lines = response.choices[0].message.content.strip().split("\n")
        cleaned = [line.strip() for line in lines if line.strip()]

        return {
            "summary": cleaned[0] if len(cleaned) > 0 else "",
            "biological_mechanism": cleaned[1] if len(cleaned) > 1 else "",
            "clinical_impact": cleaned[2] if len(cleaned) > 2 else "",
            "dosing_guidance": "Follow CPIC recommendations based on genotype and phenotype.",
            "confidence": "High",
        }
    except Exception as e:
        return {
            "summary": f"{gene} may alter response to {drug}.",
            "biological_mechanism": "Genetic variation can change drug metabolism.",
            "clinical_impact": "Treatment efficacy or safety may differ for this patient.",
            "dosing_guidance": "Use genotype-guided dosing and monitor closely."
        }
