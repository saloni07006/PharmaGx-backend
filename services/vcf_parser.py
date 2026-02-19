# ==========================================
# VCF Parsing Service
# ==========================================

TARGET_GENES = [
    "CYP2D6",
    "CYP2C19",
    "CYP2C9",
    "SLCO1B1",
    "TPMT",
    "DPYD"
]


class VCFValidationError(Exception):
    pass


def parse_vcf(file_content: str, return_warnings: bool = False):
    """
    Parse VCF file content and extract pharmacogenomic variants.
    """

    variants = []
    warnings = []

    lines = file_content.splitlines()

    if not lines:
        raise VCFValidationError("The uploaded VCF file is empty.")

    has_chrom_header = any(line.startswith("#CHROM") for line in lines)
    if not has_chrom_header:
        raise VCFValidationError("Missing required VCF header line (#CHROM).")

    malformed_rows = 0
    data_rows = 0

    for line in lines:
        if not line.strip():
            continue

        if line.startswith("#"):
            continue

        data_rows += 1

        columns = line.split("\t")

        if len(columns) < 8:
            malformed_rows += 1
            continue

        chrom = columns[0]
        pos = columns[1]
        rsid = columns[2]
        info_field = columns[7]

        info_parts = {}
        for item in info_field.split(";"):
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            info_parts[key] = value

        gene = info_parts.get("GENE")
        star = info_parts.get("STAR")

        if not gene:
            warnings.append("One or more variants are missing GENE annotation and were skipped.")
            continue

        if not star:
            star = "Unknown"
            warnings.append(f"STAR annotation missing for {gene}; defaulted to Unknown.")

        if not rsid or rsid == ".":
            rsid = f"{chrom}:{pos}"
            warnings.append("One or more variants were missing RSID and were labeled using CHROM:POS.")

        if gene in TARGET_GENES:
            variants.append({
                "gene": gene,
                "rsid": rsid,
                "star": star
            })

    if data_rows == 0:
        raise VCFValidationError("No variant records were found in the VCF file.")

    if malformed_rows > 0:
        warnings.append(f"{malformed_rows} malformed variant record(s) were skipped.")

    deduped_warnings = list(dict.fromkeys(warnings))

    if return_warnings:
        return variants, deduped_warnings

    return variants
