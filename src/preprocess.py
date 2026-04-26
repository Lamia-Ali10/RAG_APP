import re
from data_loader import load_all_documents

# ============================================================
# STEP 1 — FIX ENCODING ISSUES
# ============================================================

def fix_encoding(text: str) -> str:
    """
    Fix common encoding artifacts found in your files.
    Found in 22/31 files.
    """
    encoding_map = {
        "\u00a0": " ",    # non-breaking space
        "\u2019": "'",    # curly apostrophe    →  '
        "\u2018": "'",    # curly quote         →  '
        "\u201c": '"',    # left double quote   →  "
        "\u201d": '"',    # right double quote  →  "
        "\u2013": "-",    # en dash             →  -
        "\u2014": "-",    # em dash             →  -
    }
    for bad, good in encoding_map.items():
        text = text.replace(bad, good)
    return text

# ============================================================
# STEP 2 — REMOVE URLs
# ============================================================

def remove_urls(text: str) -> str:
    """
    Remove any line that contains a URL — whole line removed.
    Found in 5/31 files. Only 2 URLs in your actual data.
    """
    lines = text.split("\n")
    lines = [
        line for line in lines
        if not re.search(r"http\S+|www\.\S+", line)
    ]
    return "\n".join(lines)

# ============================================================
# STEP 3 — REMOVE SPECIAL CHARACTERS
# ============================================================

def remove_special_chars(text: str) -> str:
    """
    Remove special symbols found in your files.
    Found in 2/31 files (covid19_who, tuberculosis_who).
    Keeps normal punctuation → . , ! ? : ; ( ) - ' "
    """
    text = re.sub(r"[|~^•*#@<>{}\\]", " ", text)
    return text

# ============================================================
# STEP 4 — REMOVE SHORT LINES
# ============================================================

def remove_short_lines(text: str) -> str:
    """
    Remove lines that are too short to be meaningful.
    Found in 25/31 files (navigation/menu leftovers).
    Threshold = 40 characters.
    """
    lines = text.split("\n")
    lines = [
        line for line in lines
        if len(line.strip()) == 0    # keep blank lines (paragraph breaks)
        or len(line.strip()) >= 40   # keep long meaningful lines
    ]
    return "\n".join(lines)

# ============================================================
# STEP 5 — FIX EXTRA SPACES & NORMALIZE WHITESPACE
# ============================================================

def fix_whitespace(text: str) -> str:
    """
    Fix extra spaces and normalize blank lines.
    Found in 9/31 files.
    """
    # Collapse multiple spaces → single space
    text = re.sub(r" {2,}", " ", text)

    # Normalize line endings
    text = re.sub(r"\r\n|\r", "\n", text)

    # Collapse more than 2 blank lines → single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip each line
    lines = [line.strip() for line in text.split("\n")]
    text  = "\n".join(lines)

    # Final strip
    return text.strip()

# ============================================================
# MAIN PREPROCESS FUNCTION
# ============================================================

def preprocess(text: str) -> str:
    """
    Full cleaning pipeline:
    1. Fix encoding
    2. Remove URLs
    3. Remove special chars
    4. Remove short lines
    5. Fix whitespace
    """
    text = fix_encoding(text)
    text = remove_urls(text)
    text = remove_special_chars(text)
    text = remove_short_lines(text)
    text = fix_whitespace(text)
    return text

# ============================================================
# PREPROCESS ALL DOCUMENTS
# ============================================================

def preprocess_all(documents: list[dict]) -> list[dict]:
    """
    Apply cleaning to all loaded documents.
    """
    print("=" * 60)
    print("🧹  PREPROCESSING ALL DOCUMENTS")
    print("=" * 60)

    current_disease = None

    for doc in documents:
        if doc["disease"] != current_disease:
            current_disease = doc["disease"]
            print(f"\n🦠  {doc['disease'].upper()}")

        raw_length   = len(doc["content"])
        clean_text   = preprocess(doc["content"])
        clean_length = len(clean_text)

        doc["content"] = clean_text
        doc["length"]  = clean_length

        print(f"  ✅ {doc['source'].upper():<6}"
              f" | before: {raw_length:>7,}"
              f" → after: {clean_length:>7,}"
              f" | removed: {raw_length - clean_length:>5,} chars")

    total_clean = sum(d["length"] for d in documents)
    print("\n" + "=" * 60)
    print("📊  CLEANING SUMMARY")
    print("=" * 60)
    print(f"  📄 Total documents  : {len(documents)}")
    print(f"  ✨ Total clean chars: {total_clean:,}")
    print("=" * 60)

    return documents

# ============================================================
# SEMANTIC CHUNKING
# ============================================================

MIN_CHUNK      = 150   # minimum chars
MAX_CHUNK      = 800   # maximum chars
TARGET_SENTENCES = 4   # target sentences per chunk

def split_into_chunks(text: str) -> list[str]:
    """
    Split text into semantic chunks using sentence grouping.
    Groups sentences into chunks of ~4 sentences each.
    Perfect for short-paragraph medical text.
    """

    # ── Handle tiny files → keep as one chunk ────────────
    if len(text) < MIN_CHUNK:
        return [text]

    # ── Step 1: Split into sentences ─────────────────────
    # First normalize newlines to spaces within paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text)]
    paragraphs = [p for p in paragraphs if len(p) > 0]

    # Join paragraphs with space, split into sentences
    all_sentences = []
    for para in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", para.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        all_sentences.extend(sentences)

    if not all_sentences:
        return [text]

    # ── Step 2: Group sentences into chunks ───────────────
    chunks  = []
    current = []
    current_len = 0

    for sentence in all_sentences:
        current.append(sentence)
        current_len += len(sentence)

        # Save chunk when we hit target size or max chars
        if len(current) >= TARGET_SENTENCES or current_len >= MAX_CHUNK:
            chunk_text = " ".join(current).strip()
            if len(chunk_text) >= MIN_CHUNK:
                chunks.append(chunk_text)
            elif chunks:
                # Too small → merge with previous chunk
                chunks[-1] = chunks[-1] + " " + chunk_text
            else:
                chunks.append(chunk_text)
            current     = []
            current_len = 0

    # ── Save remaining sentences ──────────────────────────
    if current:
        chunk_text = " ".join(current).strip()
        if chunks and len(chunk_text) < MIN_CHUNK:
            # Too small → merge with previous
            chunks[-1] = chunks[-1] + " " + chunk_text
        else:
            chunks.append(chunk_text)

    # ── Final safety check ────────────────────────────────
    if not chunks:
        return [text]

    return chunks

def chunk_document(doc: dict) -> list[dict]:
    """
    Chunk a single document and attach metadata to each chunk.
    """
    chunks     = split_into_chunks(doc["content"])
    chunk_list = []

    for i, chunk_text in enumerate(chunks):
        chunk_list.append({
            "chunk_id" : f"{doc['disease']}_{doc['source']}_{i}",
            "disease"  : doc["disease"],
            "source"   : doc["source"],
            "content"  : chunk_text,
            "length"   : len(chunk_text)
        })

    return chunk_list


def chunk_all(documents: list[dict]) -> list[dict]:
    """
    Chunk ALL documents and return flat list of all chunks.
    """
    all_chunks      = []
    current_disease = None

    print("=" * 60)
    print("✂️   SEMANTIC CHUNKING ALL DOCUMENTS")
    print(f"     MIN chunk size : {MIN_CHUNK} chars")
    print(f"     MAX chunk size : {MAX_CHUNK} chars")
    print("=" * 60)

    for doc in documents:
        if doc["disease"] != current_disease:
            current_disease = doc["disease"]
            print(f"\n🦠  {doc['disease'].upper()}")

        chunks = chunk_document(doc)
        all_chunks.extend(chunks)

        avg_size = sum(c["length"] for c in chunks) // max(len(chunks), 1)

        print(f"  ✅ {doc['source'].upper():<6}"
              f" | chunks: {len(chunks):>3}"
              f" | avg size: {avg_size:>5} chars")

    # ── Summary ──────────────────────────────────────────────
    total_chunks = len(all_chunks)
    avg_chunk    = sum(c["length"] for c in all_chunks) // max(total_chunks, 1)

    print("\n" + "=" * 60)
    print("📊  CHUNKING SUMMARY")
    print("=" * 60)
    print(f"  ✂️  Total chunks     : {total_chunks}")
    print(f"  📏 Avg chunk size   : {avg_chunk} chars")
    print(f"  📄 Total documents  : {len(documents)}")
    print("=" * 60)

    return all_chunks

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # 1️⃣ Load
    raw_docs    = load_all_documents()

    # 2️⃣ Clean
    clean_docs  = preprocess_all(raw_docs)

    # 3️⃣ Chunk
    all_chunks  = chunk_all(clean_docs)

    # 4️⃣ Preview 3 chunks from first doc
    print(f"\n🔍  SAMPLE CHUNKS PREVIEW")
    print("=" * 60)
    sample = [c for c in all_chunks if c["disease"] == "asthma"][:3]

    for i, chunk in enumerate(sample):
        print(f"\n📦  Chunk {i+1}")
        print(f"  ID      : {chunk['chunk_id']}")
        print(f"  Disease : {chunk['disease']}")
        print(f"  Source  : {chunk['source']}")
        print(f"  Length  : {chunk['length']} chars")
        print(f"  Content : {chunk['content'][:200]}...")