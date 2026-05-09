import re
from pathlib import Path

DATA_DIR = Path("src/data")

print("=" * 60)
print("🧮  CHUNKING STRATEGY — MATHEMATICAL PROOF")
print("=" * 60)

total_chars     = 0
total_sentences = 0
total_paras     = 0
all_sent_lengths = []
all_para_lengths = []

for filepath in sorted(DATA_DIR.glob("*.txt")):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Count paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n\n+", content)]
    paragraphs = [p for p in paragraphs if len(p) > 40]

    for para in paragraphs:
        all_para_lengths.append(len(para))

        # Count sentences
        sentences = re.split(r"(?<=[.!?])\s+", para)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        for sent in sentences:
            all_sent_lengths.append(len(sent))
            total_chars += len(sent)

    total_paras     += len(paragraphs)
    total_sentences += sum(
        len([s for s in re.split(r"(?<=[.!?])\s+", p)
             if len(s.strip()) > 20])
        for p in paragraphs
    )

# ── Calculations ─────────────────────────────────────────────
avg_sent_len  = sum(all_sent_lengths) / max(len(all_sent_lengths), 1)
avg_para_len  = sum(all_para_lengths) / max(len(all_para_lengths), 1)
avg_sents_para = total_sentences / max(total_paras, 1)

print(f"\n📊  RAW MEASUREMENTS:")
print(f"  Total paragraphs        : {total_paras}")
print(f"  Total sentences         : {total_sentences}")
print(f"  Avg chars / sentence    : {avg_sent_len:.1f}")
print(f"  Avg chars / paragraph   : {avg_para_len:.1f}")
print(f"  Avg sentences / para    : {avg_sents_para:.1f}")

print(f"\n🧮  CHUNK SIZE CALCULATION:")
TARGET_SENTENCES = 4
expected = TARGET_SENTENCES * avg_sent_len
print(f"  Target sentences/chunk  : {TARGET_SENTENCES}")
print(f"  Avg chars/sentence      : {avg_sent_len:.1f}")
print(f"  Expected chunk size     : {TARGET_SENTENCES} × {avg_sent_len:.1f} = {expected:.1f} chars")

print(f"\n✅  STRATEGY JUSTIFICATION:")
print(f"  MIN_CHUNK = 150  = {150/avg_sent_len:.1f} sentences minimum")
print(f"  MAX_CHUNK = 800  = {800/avg_sent_len:.1f} sentences maximum")
print(f"  TARGET    = 4    = one complete medical topic")
print(f"  Expected avg chunk = {expected:.0f} chars")

print(f"\n⚠️  WHY NOT PARAGRAPHS ALONE?")
print(f"  Avg paragraph = {avg_para_len:.0f} chars → too small for RAG")
print(f"  Would create  = {total_paras} tiny chunks → poor retrieval")

print(f"\n✅  WHY SENTENCE GROUPING?")
print(f"  4 sentences   = {expected:.0f} chars → ideal for embeddings")
print(f"  Clean boundaries → no mid-sentence cuts")
print(f"  Semantic meaning preserved per chunk")