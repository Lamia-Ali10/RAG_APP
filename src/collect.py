import os
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)  # Create /data folder if not exists

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# ============================================================
# ALL 50 URLs  (10 diseases × 5 sources)
# ============================================================

URLS = {

    # ── ASTHMA ──────────────────────────────────────────────
    "asthma_who" : "https://www.who.int/news-room/fact-sheets/detail/asthma",
    "asthma_nih" : "https://medlineplus.gov/asthma.html",
    "asthma_nhs" : "https://www.nhs.uk/conditions/asthma/",

    # ── CANCER ──────────────────────────────────────────────
    "cancer_who" : "https://www.who.int/news-room/fact-sheets/detail/cancer",
    "cancer_nih" : "https://medlineplus.gov/cancer.html",
    "cancer_nhs" : "https://www.nhs.uk/conditions/cancer/",

    # ── COVID-19 ────────────────────────────────────────────
    "covid19_who" : "https://www.who.int/news-room/fact-sheets/detail/coronavirus-disease-(covid-19)",
    "covid19_nhs" : "https://www.nhs.uk/conditions/covid-19/",

    # ── DENGUE ──────────────────────────────────────────────
    "dengue_who" : "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
    "dengue_nih" : "https://medlineplus.gov/dengue.html",
    "dengue_nhs" : "https://www.nhs.uk/conditions/dengue/",

    # ── DIABETES ────────────────────────────────────────────
    "diabetes_who" : "https://www.who.int/news-room/fact-sheets/detail/diabetes",
    "diabetes_nih" : "https://medlineplus.gov/diabetes.html",
    "diabetes_nhs" : "https://www.nhs.uk/conditions/diabetes/",

    # ── HEART DISEASE ───────────────────────────────────────
    "heart_disease_who" : "https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)",
    "heart_disease_nih" : "https://medlineplus.gov/heartdiseases.html",
    "heart_disease_nhs" : "https://www.nhs.uk/conditions/coronary-heart-disease/",
    "heart_disease_cdc" : "https://www.cdc.gov/heartdisease/index.htm",

    # ── HYPERTENSION ────────────────────────────────────────
    "hypertension_who" : "https://www.who.int/news-room/fact-sheets/detail/hypertension",
    "hypertension_nih" : "https://medlineplus.gov/highbloodpressure.html",
    "hypertension_nhs" : "https://www.nhs.uk/conditions/high-blood-pressure-hypertension/",

    # ── MALARIA ─────────────────────────────────────────────
    "malaria_who" : "https://www.who.int/news-room/fact-sheets/detail/malaria",
    "malaria_nih" : "https://medlineplus.gov/malaria.html",
    "malaria_nhs" : "https://www.nhs.uk/conditions/malaria/",

    # ── STROKE ──────────────────────────────────────────────
    "stroke_who" : "https://www.who.int/news-room/fact-sheets/detail/the-top-10-causes-of-death",
    "stroke_nih" : "https://medlineplus.gov/stroke.html",
    "stroke_nhs" : "https://www.nhs.uk/conditions/stroke/",

    # ── TUBERCULOSIS ────────────────────────────────────────
    "tuberculosis_who" : "https://www.who.int/news-room/fact-sheets/detail/tuberculosis",
    "tuberculosis_nih" : "https://medlineplus.gov/tuberculosis.html",
    "tuberculosis_nhs" : "https://www.nhs.uk/conditions/tuberculosis-tb/",
    "tuberculosis_cdc" : "https://www.cdc.gov/tb/index.html",
}
# ============================================================
# SCRAPER FUNCTION
# ============================================================

def scrape_page(url: str) -> str | None:
    """
    Scrape a URL and return clean text content.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # ── Remove junk tags ──────────────────────────────────
        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "form", "button",
                          "iframe", "noscript"]):
            tag.decompose()

        # ── Extract main content ──────────────────────────────
        # Try to find the main article/content area
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", {"id"   : "main-content"})
            or soup.find("div", {"class": "content"})
            or soup.find("div", {"class": "main"})
            or soup.body
        )

        if main:
            # Get all text, clean whitespace
            lines = []
            for element in main.find_all(
                ["h1","h2","h3","h4","p","li","td","th"]
            ):
                text = element.get_text(separator=" ", strip=True)
                if text and len(text) > 30:   # skip tiny fragments
                    lines.append(text)

            return "\n\n".join(lines)

        return None

    except requests.exceptions.Timeout:
        print(f"    ⏱️  Timeout")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"    🚫 HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None


# ============================================================
# SAVE FUNCTION
# ============================================================

def save_text(filename: str, content: str) -> None:
    """
    Save text content to /data folder.
    """
    filepath = DATA_DIR / f"{filename}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# MAIN COLLECTOR
# ============================================================

def collect_all() -> None:

    success = []
    failed  = []

    print("=" * 60)
    print("🌐  COLLECTING ALL DISEASE DATA")
    print(f"📂  Saving to : {DATA_DIR}")
    print(f"📄  Total URLs: {len(URLS)}")
    print("=" * 60)

    for name, url in URLS.items():

        disease, source = name.rsplit("_", 1)
        print(f"\n🦠  {disease.upper()} | 📚 {source.upper()}")
        print(f"    🔗 {url}")

        content = scrape_page(url)

        if content and len(content) > 100:
            save_text(name, content)
            success.append(name)
            print(f"    ✅ Saved → {name}.txt ({len(content):,} chars)")
        else:
            failed.append(name)
            print(f"    ❌ Failed or empty → skipping")

        # ── Be polite to servers ──────────────────────────────
        time.sleep(2)

    # ── Final Summary ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("📊  COLLECTION SUMMARY")
    print("=" * 60)
    print(f"  ✅ Success : {len(success)} files saved")
    print(f"  ❌ Failed  : {len(failed)} files")

    if failed:
        print(f"\n  ⚠️  Failed URLs:")
        for f in failed:
            print(f"     ✗ {f}")

    print(f"\n  📂 All files saved in: {DATA_DIR}")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    collect_all()