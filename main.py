# ======================================================
# PharmaGuard AI - FastAPI Main Application
# ======================================================

import os
import sys
from datetime import datetime

# ------------------------------------------------------
# Fix Python path (Prevents ModuleNotFoundError)
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------
# Imports
# ------------------------------------------------------
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.predictor import predict_risk
from services.vcf_parser import parse_vcf, VCFValidationError
from services.genotype_service import build_diplotypes
from services.phenotype_mapper import determine_phenotype
from services.rule_engine import rule_based_risk
from services.response_builder import build_final_response



# ======================================================
# FastAPI App Initialization
# ======================================================

app = FastAPI(
    title="PharmaGuard AI",
    description="Pharmacogenomic Risk Prediction System",
    version="1.0.0"
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# Drug → Gene Mapping
# ======================================================

DRUG_GENE_MAP = {
    "CODEINE": "CYP2D6",
    "WARFARIN": "CYP2C9",
    "CLOPIDOGREL": "CYP2C19",
    "SIMVASTATIN": "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "FLUOROURACIL": "DPYD"
}


def user_friendly_error(code: str, message: str, hint: str):
    return {
        "code": code,
        "message": message,
        "user_message": message,
        "hint": hint
    }


# ======================================================
# Request Schema (Direct ML Testing)
# ======================================================

class PredictionRequest(BaseModel):
    drug: str
    phenotype: str


# ======================================================
# Health Check Endpoint
# ======================================================

@app.get("/")
def root():
    return {
        "status": "PharmaGuard AI Backend Running",
        "message": "System Ready"
    }


# ======================================================
# Direct ML Prediction Endpoint (For Testing)
# ======================================================

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        risk_label, confidence = predict_risk(
            drug=request.drug.upper(),
            phenotype=request.phenotype.upper()
        )

        return {
            "drug": request.drug.upper(),
            "phenotype": request.phenotype.upper(),
            "predicted_risk": risk_label,
            "confidence_score": confidence
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# Full VCF Pipeline Endpoint
# ======================================================

@app.post("/analyze")
async def analyze_vcf(
    file: UploadFile = File(...),
    drug: str = Form(...)
):
    """
    Upload VCF + Drug Name
    """

    try:
        # ----------------------------
        # Step 1: Validate Drug
        # ----------------------------
        drug = drug.upper()

        if drug not in DRUG_GENE_MAP:
            raise HTTPException(
                status_code=400,
                detail=user_friendly_error(
                    code="UNSUPPORTED_DRUG",
                    message="The selected drug is not supported for pharmacogenomic analysis.",
                    hint="Please choose one of the supported drugs from the dropdown list."
                )
            )

        # ----------------------------
        # Step 2: Read VCF File
        # ----------------------------
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail=user_friendly_error(
                    code="EMPTY_FILE",
                    message="The uploaded VCF file is empty.",
                    hint="Upload a valid .vcf file that contains variant records."
                )
            )

        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail=user_friendly_error(
                    code="INVALID_ENCODING",
                    message="The uploaded VCF file encoding is not valid UTF-8.",
                    hint="Export or save the VCF file in UTF-8 format and try again."
                )
            )

        # ----------------------------
        # Step 3: Parse VCF
        # ----------------------------
        try:
            variants, annotation_warnings = parse_vcf(content, return_warnings=True)
        except VCFValidationError as vcf_error:
            raise HTTPException(
                status_code=400,
                detail=user_friendly_error(
                    code="INVALID_VCF",
                    message=str(vcf_error),
                    hint="Ensure the file follows VCF format and includes the #CHROM header plus tab-separated variant rows."
                )
            )

        if not variants:
            raise HTTPException(
                status_code=400,
                detail=user_friendly_error(
                    code="NO_PGX_VARIANTS",
                    message="No supported pharmacogenomic variants were found in the uploaded file.",
                    hint="Verify that the VCF includes GENE annotations for CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, or DPYD."
                )
            )

        # ----------------------------
        # Step 4: Build Diplotypes
        # ----------------------------
        diplotypes = build_diplotypes(variants)

        primary_gene = DRUG_GENE_MAP[drug]
        diplotype = diplotypes.get(primary_gene, "Unknown")

        # ----------------------------
        # Step 5: Determine Phenotype
        # ----------------------------
        phenotype = determine_phenotype(primary_gene, diplotype)

       # ----------------------------
        # Step 6: Hybrid Risk System
        # ----------------------------

        # 1️. Rule-based (clinical authority)
        rule_risk, severity = rule_based_risk(drug, phenotype)

        # 2. ML-based (probabilistic validation)
        ml_risk, confidence = predict_risk(drug, phenotype)

        # 3️. Final decision → Always trust rule engine
        final_risk = rule_risk
        confidence_score = confidence
        
        # ----------------------------
        # Build Final Structured JSON
        # ----------------------------

        final_response = build_final_response(
            drug=drug,
            primary_gene=primary_gene,
            diplotype=diplotype,
            phenotype=phenotype,
            variants=variants,
            rule_risk=final_risk,
            severity=severity,
            confidence=confidence_score,
            annotation_warnings=annotation_warnings
        )

        return final_response



       

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# Quick GET Test
# ======================================================

@app.get("/test-prediction")
def test_prediction(drug: str, phenotype: str):
    try:
        risk_label, confidence = predict_risk(
            drug=drug.upper(),
            phenotype=phenotype.upper()
        )

        return {
            "drug": drug.upper(),
            "phenotype": phenotype.upper(),
            "predicted_risk": risk_label,
            "confidence_score": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
