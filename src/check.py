import re
from pathlib import Path

DATA_DIR = Path("src/data")

print("=" * 60)
print("📊  PARAGRAPH & SENTENCE ANALYSIS")
print("=" * 60)

total_paragraphs = 0
total_sentences  = 0
total_files      = 0

for filepath in sorted(DATA_DIR.glob("*.txt")):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n\n+", content)]
    paragraphs = [p for p in paragraphs if len(p) > 40]

    # Count sentences per paragraph
    sentences_per_para = []
    for para in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", para)
        sentences = [s for s in sentences if len(s) > 20]
        sentences_per_para.append(len(sentences))

    avg_sentences = sum(sentences_per_para) / max(len(sentences_per_para), 1)

    total_paragraphs += len(paragraphs)
    total_sentences  += sum(sentences_per_para)
    total_files      += 1

    print(f"\n📄  {filepath.name}")
    print(f"    Paragraphs        : {len(paragraphs)}")
    print(f"    Avg sentences/para: {avg_sentences:.1f}")
    print(f"    Min sentences     : {min(sentences_per_para) if sentences_per_para else 0}")
    print(f"    Max sentences     : {max(sentences_per_para) if sentences_per_para else 0}")

print("\n" + "=" * 60)
print("📊  OVERALL STATS")
print("=" * 60)
print(f"  Total paragraphs       : {total_paragraphs}")
print(f"  Total sentences        : {total_sentences}")
print(f"  Avg sentences/para     : {total_sentences / max(total_paragraphs, 1):.1f}")
print(f"  Avg paragraphs/doc     : {total_paragraphs / max(total_files, 1):.1f}")