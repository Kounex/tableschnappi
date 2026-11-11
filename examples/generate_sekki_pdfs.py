"""
Generate one PDF per sekki (24 total).

Requires:  pip install fpdf2 requests
Run once:  python3 examples/generate_sekki_pdfs.py

Output:    examples/sekki_pdfs/  (24 PDF files)
"""
import os
import sys
import urllib.request
from pathlib import Path
from fpdf import FPDF

# ── Import sekki content ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from sekki_data import SEKKI

# Both are overridable so a pipeline step can point this at its output
# artifact and at a font it has already fetched. The sekki pipeline sets
# them; before this they were ignored and the step produced an empty
# artifact while still reporting success.
OUT_DIR = Path(os.environ.get("SEKKI_PDF_OUT") or Path(__file__).parent / "sekki_pdfs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path(__file__).parent / "fonts"
FONT_DIR.mkdir(exist_ok=True)

# ── Download NotoSansJP if missing ─────────────────────────────────────────────
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
FONT_PATH = Path(os.environ.get("NOTO_FONT_PATH") or FONT_DIR / "NotoSansJP.ttf")

if not FONT_PATH.exists():
    print("Downloading NotoSansJP font...")
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    print("  Done.")

# ── Palette ────────────────────────────────────────────────────────────────────
SAKURA_RED    = (139,  0,  0)   # deep red
GOLD          = (180, 140, 60)  # warm gold
INK           = ( 30, 28, 25)  # near-black
CREAM         = (253, 249, 242) # warm white
LIGHT_ROSE    = (248, 235, 235)


class SekkiPDF(FPDF):
    def __init__(self, sekki: dict):
        super().__init__()
        self.s = sekki
        self.add_font("Noto", "", str(FONT_PATH))
        self.add_font("Noto", "B", str(FONT_PATH))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _rgb(self, color: tuple, fill=False):
        if fill:
            self.set_fill_color(*color)
        else:
            self.set_text_color(*color)

    def _rule(self, color=GOLD, thickness=0.5):
        self.set_draw_color(*color)
        self.set_line_width(thickness)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    # ── cover page ────────────────────────────────────────────────────────────

    def cover(self):
        self.add_page()
        self.set_auto_page_break(False)

        # cream background
        self._rgb(CREAM, fill=True)
        self.rect(0, 0, 210, 297, "F")

        # red stripe top
        self._rgb(SAKURA_RED, fill=True)
        self.rect(0, 0, 210, 8, "F")

        # red stripe bottom
        self.rect(0, 289, 210, 8, "F")

        # sekki number badge
        self._rgb(SAKURA_RED, fill=True)
        self.rect(15, 20, 32, 32, "F")
        self._rgb((255, 255, 255))
        self.set_font("Noto", "B", 10)
        self.set_xy(15, 23)
        self.cell(32, 6, f"第 {self.s['number']} 節気", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Noto", "B", 18)
        self.set_x(15)
        self.cell(32, 14, f"{self.s['number']:02d}", align="C")

        # large kanji
        self._rgb(INK)
        self.set_font("Noto", "B", 72)
        self.set_xy(55, 15)
        self.cell(140, 50, self.s["kanji"], align="C")

        # romaji + english
        self._rgb(SAKURA_RED)
        self.set_font("Noto", "B", 22)
        self.set_xy(15, 70)
        self.cell(180, 10, self.s["romaji"], align="C", new_x="LMARGIN", new_y="NEXT")

        self._rgb(INK)
        self.set_font("Noto", "", 14)
        self.set_x(15)
        self.cell(180, 8, self.s["english"], align="C")

        # gold rule
        self.set_y(95)
        self._rule()

        # date range
        self._rgb(GOLD)
        self.set_font("Noto", "", 11)
        self.set_x(15)
        next_s = SEKKI[(self.s["number"]) % 24]
        self.cell(180, 8,
                  f"Approx. {self.s['start_month']}/{self.s['start_day']} – "
                  f"{next_s['start_month']}/{next_s['start_day']}  •  15 days",
                  align="C", new_x="LMARGIN", new_y="NEXT")

        # haiku box
        self._rgb(LIGHT_ROSE, fill=True)
        self.set_fill_color(*LIGHT_ROSE)
        self.set_y(112)
        self.set_x(30)
        self.set_font("Noto", "", 13)
        self._rgb(INK)
        for line in self.s["haiku"].split("\n"):
            self.set_x(30)
            self.cell(150, 8, line.strip(), align="C", new_x="LMARGIN", new_y="NEXT")

        # gold rule
        self.set_y(148)
        self._rule()

        # description
        self._rgb(INK)
        self.set_font("Noto", "", 11)
        self.set_x(20)
        self.multi_cell(170, 7, self.s["description"], align="J")

        # footer
        self._rgb(GOLD)
        self.set_font("Noto", "", 9)
        self.set_xy(15, 278)
        self.cell(180, 6, "桜 Sakura Japanese Restaurant  •  Seasonal Knowledge Series", align="C")

    # ── content page ─────────────────────────────────────────────────────────

    def content(self):
        self.add_page()
        self.set_auto_page_break(True, margin=18)

        # header bar
        self._rgb(SAKURA_RED, fill=True)
        self.rect(0, 0, 210, 12, "F")
        self._rgb((255, 255, 255))
        self.set_font("Noto", "B", 9)
        self.set_xy(15, 3)
        self.cell(180, 6,
                  f"{self.s['kanji']}  {self.s['romaji']}  —  {self.s['english']}",
                  align="C")

        self.set_y(18)

        # Nature Signs
        self._section_title("Signs in Nature  自然の兆し")
        self._rgb(INK)
        self.set_font("Noto", "", 11)
        for sign in self.s["nature_signs"]:
            self.set_x(20)
            self.cell(5, 7, "•")
            self.set_x(26)
            self.multi_cell(164, 7, sign, new_x="LMARGIN", new_y="NEXT")

        self.ln(3)

        # Shun Ingredients table
        self._section_title("Shun Ingredients  旬の食材")
        self._rgb(INK)
        col_w = [42, 42, 98]
        # header row
        self._rgb(SAKURA_RED, fill=True)
        self.set_font("Noto", "B", 9)
        self._rgb((255, 255, 255))
        self.set_x(15)
        for txt, w in zip(["Japanese", "English", "Why it peaks now"], col_w):
            self.cell(w, 7, txt, border=0, align="C", fill=True)
        self.ln()
        # data rows
        self.set_font("Noto", "", 9)
        for i, ing in enumerate(self.s["shun_ingredients"]):
            fill = i % 2 == 0
            self._rgb(LIGHT_ROSE if fill else CREAM, fill=True)
            self._rgb(INK)
            self.set_x(15)
            self.cell(col_w[0], 6, ing["name_ja"], border=0, fill=fill)
            self.cell(col_w[1], 6, ing["name_en"], border=0, fill=fill)
            # note may be long — use multi_cell workaround
            x = self.get_x()
            y = self.get_y()
            self.multi_cell(col_w[2], 6, ing["note"], border=0, fill=fill,
                            new_x="LMARGIN", new_y="NEXT")
            # align next row Y if multi_cell advanced it
        self.ln(3)

        # Health Wisdom
        self._section_title("Traditional Wisdom  伝統的な知恵")
        self.set_font("Noto", "", 11)
        self._rgb(INK)
        self.set_x(20)
        self.multi_cell(170, 7, self.s["health_wisdom"], align="J",
                        new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        # Restaurant recommendations
        self._section_title("At Sakura Restaurant  桜レストランにて")
        self.set_font("Noto", "", 11)
        self._rgb(INK)
        for rec in self.s["sakura_recommendations"]:
            self.set_x(20)
            self.set_font("Noto", "B", 10)
            self._rgb(SAKURA_RED)
            self.cell(6, 7, "旬")
            self.set_font("Noto", "", 11)
            self._rgb(INK)
            self.multi_cell(164, 7, rec, new_x="LMARGIN", new_y="NEXT")

        # footer
        self.set_y(-14)
        self._rgb(LIGHT_ROSE, fill=True)
        self.rect(0, 283, 210, 14, "F")
        self._rgb(GOLD)
        self.set_font("Noto", "", 8)
        self.set_xy(15, 286)
        self.cell(180, 6,
                  f"二十四節気 no. {self.s['number']}  •  桜 Sakura Japanese Restaurant  •  "
                  f"Seasonal Knowledge Series", align="C")

    def _section_title(self, title: str):
        self._rgb(INK)
        self.set_font("Noto", "B", 13)
        self.set_x(15)
        self.cell(180, 8, title, new_x="LMARGIN", new_y="NEXT")
        self._rule(SAKURA_RED, 0.3)
        self.ln(1)


def generate_all():
    for sekki in SEKKI:
        pdf = SekkiPDF(sekki)
        pdf.cover()
        pdf.content()
        fname = OUT_DIR / f"{sekki['number']:02d}_{sekki['id']}.pdf"
        pdf.output(str(fname))
        print(f"  ✓  {fname.name}")

    print(f"\nGenerated {len(SEKKI)} PDFs → {OUT_DIR}/")


if __name__ == "__main__":
    print("Generating sekki PDFs...")
    generate_all()
