from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent / "data"

AVAILABLE_FILES = [

    # ── ASTHMA ──────────────────────────────────────────────
    "asthma_nhs",
    "asthma_nih",
    "asthma_who",

    # ── CANCER ──────────────────────────────────────────────
    "cancer_nhs",
    "cancer_nih",
    "cancer_who",

    # ── COVID-19 ────────────────────────────────────────────
    "covid19_nhs",
    "covid19_who",

    # ── DENGUE ──────────────────────────────────────────────
    "dengue_nhs",
    "dengue_nih",
    "dengue_who",

    # ── DIABETES ────────────────────────────────────────────
    "diabetes_nhs",
    "diabetes_nih",
    "diabetes_who",

    # ── HEART DISEASE ───────────────────────────────────────
    "heart_disease_cdc",
    "heart_disease_nhs",
    "heart_disease_nih",
    "heart_disease_who",

    # ── HYPERTENSION ────────────────────────────────────────
    "hypertension_nhs",
    "hypertension_nih",
    "hypertension_who",

    # ── MALARIA ─────────────────────────────────────────────
    "malaria_nhs",
    "malaria_nih",
    "malaria_who",

    # ── STROKE ──────────────────────────────────────────────
    "stroke_nhs",
    "stroke_nih",
    "stroke_who",

    # ── TUBERCULOSIS ────────────────────────────────────────
    "tuberculosis_cdc",
    "tuberculosis_nhs",
    "tuberculosis_nih",
    "tuberculosis_who",
]

# ============================================================
# LOAD SINGLE FILE
# ============================================================

def load_single_file(filepath: Path) -> dict | None:
    """
    Load a single .txt file and return a structured dict.
    """
    if not filepath.exists():
        print(f"  ⚠️  Missing : {filepath.name}")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        print(f"  ⚠️  Empty   : {filepath.name}")
        return None

    # ── Parse disease + source from filename ─────────────────
    stem    = filepath.stem          # e.g. "heart_disease_who"
    parts   = stem.split("_")
    source  = parts[-1]              # "who"
    disease = "_".join(parts[:-1])   # "heart_disease"

    return {
        "disease"  : disease,
        "source"   : source,
        "filename" : filepath.name,
        "filepath" : str(filepath),
        "content"  : content.strip(),
        "length"   : len(content.strip())
    }

# ============================================================
# LOAD ALL DOCUMENTS
# ============================================================

def load_all_documents() -> list[dict]:
    """
    Load all 31 available .txt files from /data directory.
    Returns a list of document dicts.
    """
    documents       = []
    current_disease = None

    print("=" * 60)
    print("📥  LOADING ALL DISEASE DOCUMENTS")
    print(f"📂  Data folder : {DATA_DIR}")
    print(f"📄  Total files : {len(AVAILABLE_FILES)}")
    print("=" * 60)

    for name in AVAILABLE_FILES:
        filepath = DATA_DIR / f"{name}.txt"

        # ── Parse for display ─────────────────────────────────
        parts   = name.split("_")
        source  = parts[-1]
        disease = "_".join(parts[:-1])

        # ── Print disease header when it changes ──────────────
        if disease != current_disease:
            current_disease = disease
            print(f"\n🦠  {disease.upper()}")

        doc = load_single_file(filepath)

        if doc:
            documents.append(doc)
            print(f"  ✅ {source.upper():<6} → {doc['length']:>7,} chars")

    # ── Summary ──────────────────────────────────────────────
    total_chars = sum(d["length"] for d in documents)

    print("\n" + "=" * 60)
    print("📊  LOADING SUMMARY")
    print("=" * 60)
    print(f"  📄 Total documents  : {len(documents)}")
    print(f"  📝 Total characters : {total_chars:,}")
    print(f"  📝 Avg chars / doc  : {total_chars // max(len(documents), 1):,}")
    print("=" * 60)

    return documents

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # 1️⃣ Load all documents
    all_docs = load_all_documents()

    # 2️⃣ Preview first document
    if all_docs:
        doc = all_docs[0]
        print(f"\n🔍  PREVIEW — {doc['disease'].upper()} ({doc['source'].upper()})")
        print("=" * 60)
        print(f"  Filename : {doc['filename']}")
        print(f"  Length   : {doc['length']:,} chars")
        print(f"\n  Content Preview:\n")
        print(f"  {doc['content'][:400]}...")