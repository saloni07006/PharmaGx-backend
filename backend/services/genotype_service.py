# ==========================================
# Diplotype Builder
# ==========================================

from collections import defaultdict


def build_diplotypes(variants):
    """
    Group star alleles by gene and create diplotypes.
    """

    gene_map = defaultdict(list)

    for var in variants:
        gene_map[var["gene"]].append(var["star"])

    diplotypes = {}

    for gene, stars in gene_map.items():
        if len(stars) >= 2:
            diplotype = f"{stars[0]}/{stars[1]}"
        elif len(stars) == 1:
            diplotype = f"{stars[0]}/Unknown"
        else:
            diplotype = "Unknown"

        diplotypes[gene] = diplotype

    return diplotypes
