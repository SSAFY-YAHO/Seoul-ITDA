from pathlib import Path

import fitz


SOURCE = Path(r"C:\Users\SSAFY\Downloads\5분 동안 서울잇다의 목차를 소개합니다.pdf")
OUTPUT = Path(__file__).resolve().parent / "presentation_pages"
OUTPUT.mkdir(parents=True, exist_ok=True)

document = fitz.open(SOURCE)
for index, page in enumerate(document):
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    pixmap.save(OUTPUT / f"page-{index + 1:02d}.png")

print(f"rendered={len(document)} output={OUTPUT}")
