#!/usr/bin/env python3
"""
從 PDF 檔案抽取文字與圖片

用法：
    python extract_pdf.py input.pdf output_dir/ [--ocr] [--pages "1-3,7"]

輸出：
    output_dir/text.md      - PDF 文字內容（含 page# 標注）
    output_dir/images/      - 抽出的圖片
    output_dir/summary.md   - 頁面摘要

依賴：
    pip install pdfplumber Pillow
    # OCR 需要額外安裝：
    pip install pytesseract
    # 並安裝 Tesseract OCR 引擎

範例：
    python extract_pdf.py document.pdf ./extracted/
    python extract_pdf.py document.pdf ./extracted/ --pages "1-5,10"
    python extract_pdf.py document.pdf ./extracted/ --ocr
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


def parse_page_range(range_str: str, total_pages: int) -> list[int]:
    """
    解析頁碼範圍字串

    範例：
        "1-3,7,10-12" → [1, 2, 3, 7, 10, 11, 12]

    Args:
        range_str: 範圍字串
        total_pages: 總頁數

    Returns:
        頁碼列表（1-based）
    """
    if not range_str:
        return list(range(1, total_pages + 1))

    pages = set()
    parts = range_str.replace(" ", "").split(",")

    for part in parts:
        if "-" in part:
            start, end = part.split("-", 1)
            start = int(start)
            end = int(end)
            for i in range(start, min(end + 1, total_pages + 1)):
                if 1 <= i <= total_pages:
                    pages.add(i)
        else:
            num = int(part)
            if 1 <= num <= total_pages:
                pages.add(num)

    return sorted(pages)


def ocr_image(image, lang='chi_tra+eng'):
    """
    對圖片進行 OCR

    Args:
        image: PIL Image 物件
        lang: Tesseract 語言代碼

    Returns:
        辨識出的文字
    """
    try:
        import pytesseract
        return pytesseract.image_to_string(image, lang=lang)
    except ImportError:
        print("Warning: pytesseract not installed. OCR skipped.")
        return ""
    except Exception as e:
        print(f"Warning: OCR failed: {e}")
        return ""


def extract_pdf(pdf_path: str, output_dir: str, page_range: str = None, use_ocr: bool = False) -> dict:
    """
    從 PDF 抽取內容

    Args:
        pdf_path: PDF 檔案路徑
        output_dir: 輸出目錄
        page_range: 頁碼範圍（如 "1-3,7"）
        use_ocr: 是否使用 OCR

    Returns:
        抽取結果摘要
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(f"找不到檔案：{pdf_path}")

    # 建立輸出目錄
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # 開啟 PDF
    pdf = pdfplumber.open(str(pdf_path))
    total_pages = len(pdf.pages)

    # 解析頁碼範圍
    selected_pages = parse_page_range(page_range, total_pages)

    # 收集內容
    text_content = []
    summary_content = []
    image_count = 0

    text_content.append(f"# PDF 內容抽取：{pdf_path.name}")
    text_content.append(f"")
    text_content.append(f"- 總頁數：{total_pages}")
    text_content.append(f"- 抽取範圍：{selected_pages}")
    text_content.append(f"- OCR：{'啟用' if use_ocr else '停用'}")
    text_content.append(f"")
    text_content.append("---")
    text_content.append("")

    summary_content.append(f"# 頁面摘要：{pdf_path.name}")
    summary_content.append("")
    summary_content.append("| 頁碼 | 字數 | 圖片數 |")
    summary_content.append("|------|------|--------|")

    for page_num in selected_pages:
        page_idx = page_num - 1
        if page_idx >= len(pdf.pages):
            continue

        page = pdf.pages[page_idx]

        # 抽取文字
        page_text = page.extract_text() or ""
        char_count = len(page_text.strip())

        # 抽取圖片
        page_images = page.images
        page_image_count = len(page_images)

        # 摘要
        summary_content.append(f"| {page_num} | {char_count} | {page_image_count} |")

        # 詳細內容
        text_content.append(f"## Page {page_num}")
        text_content.append(f"[來源：page={page_num}]")
        text_content.append("")

        if page_text.strip():
            text_content.append("### 文字內容")
            text_content.append("")
            text_content.append(page_text.strip())
            text_content.append("")
        else:
            text_content.append("### 文字內容")
            text_content.append("（此頁無可抽取的文字）")
            text_content.append("")

            # 如果啟用 OCR 且無文字，嘗試 OCR
            if use_ocr:
                try:
                    # 將頁面轉為圖片
                    page_image = page.to_image(resolution=150)
                    pil_image = page_image.original

                    ocr_text = ocr_image(pil_image)
                    if ocr_text.strip():
                        text_content.append("### OCR 辨識結果")
                        text_content.append("")
                        text_content.append(ocr_text.strip())
                        text_content.append("")
                except Exception as e:
                    text_content.append(f"### OCR 失敗")
                    text_content.append(f"錯誤：{str(e)}")
                    text_content.append("")

        # 抽取圖片
        for img_idx, img in enumerate(page_images):
            try:
                # 取得圖片邊界
                x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']

                # 裁切頁面圖片
                page_image = page.to_image(resolution=150)
                cropped = page_image.original.crop((
                    int(x0 * 150 / 72),
                    int(y0 * 150 / 72),
                    int(x1 * 150 / 72),
                    int(y1 * 150 / 72)
                ))

                # 儲存圖片
                image_filename = f"page{page_num}_img{img_idx + 1}.png"
                image_path = images_dir / image_filename
                cropped.save(str(image_path))

                image_count += 1
                text_content.append(f"### 圖片 {img_idx + 1}")
                text_content.append(f"[來源：page={page_num}, image={img_idx + 1}]")
                text_content.append("")
                text_content.append(f"![{image_filename}](images/{image_filename})")
                text_content.append("")

            except Exception as e:
                text_content.append(f"### 圖片 {img_idx + 1} 抽取失敗")
                text_content.append(f"錯誤：{str(e)}")
                text_content.append("")

        text_content.append("---")
        text_content.append("")

    pdf.close()

    # 寫入檔案
    text_path = output_dir / "text.md"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_content))

    summary_path = output_dir / "summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_content))

    result = {
        "pdf_file": str(pdf_path),
        "total_pages": total_pages,
        "extracted_pages": len(selected_pages),
        "image_count": image_count,
        "ocr_enabled": use_ocr,
        "output_files": {
            "text": str(text_path),
            "summary": str(summary_path),
            "images_dir": str(images_dir)
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="從 PDF 檔案抽取文字與圖片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
    python extract_pdf.py document.pdf ./output/
    python extract_pdf.py document.pdf ./output/ --pages "1-5,10"
    python extract_pdf.py document.pdf ./output/ --ocr

頁碼範圍格式：
    "1-3"       選取第 1, 2, 3 頁
    "1,3,5"     選取第 1, 3, 5 頁
    "1-3,7,10-12" 選取第 1, 2, 3, 7, 10, 11, 12 頁
        """
    )

    parser.add_argument("pdf_path", help="PDF 檔案路徑")
    parser.add_argument("output_dir", help="輸出目錄")
    parser.add_argument("--pages", "-p", help="頁碼範圍（如 '1-3,7,10-12'）")
    parser.add_argument("--ocr", action="store_true", help="啟用 OCR（需安裝 pytesseract）")
    parser.add_argument("--list", "-l", action="store_true", help="只列出頁面清單，不抽取")

    args = parser.parse_args()

    # 只列出頁面清單
    if args.list:
        pdf = pdfplumber.open(args.pdf_path)
        print(f"檔案：{args.pdf_path}")
        print(f"總頁數：{len(pdf.pages)}")
        print("")
        print("| 頁碼 | 字數 | 圖片數 |")
        print("|------|------|--------|")
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            char_count = len(text.strip())
            image_count = len(page.images)
            print(f"| {i} | {char_count} | {image_count} |")
        pdf.close()
        return

    # 抽取內容
    try:
        result = extract_pdf(args.pdf_path, args.output_dir, args.pages, args.ocr)

        print(f"抽取完成！")
        print(f"")
        print(f"來源：{result['pdf_file']}")
        print(f"總頁數：{result['total_pages']} 頁")
        print(f"已抽取：{result['extracted_pages']} 頁")
        print(f"圖片數：{result['image_count']} 張")
        print(f"OCR：{'啟用' if result['ocr_enabled'] else '停用'}")
        print(f"")
        print(f"輸出檔案：")
        print(f"  - {result['output_files']['text']}")
        print(f"  - {result['output_files']['summary']}")
        print(f"  - {result['output_files']['images_dir']}/")

    except FileNotFoundError as e:
        print(f"錯誤：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"抽取失敗：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
