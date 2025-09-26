import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path

# --- CONFIGURATION ---

# 1. SET THIS to the full path of your manga PDF file.
INPUT_PDF = "period/blue-period-20.pdf"

# 2. SET THIS to the desired name for the cleaned output file.
OUTPUT_PDF = "manga_cleaned.pdf"

# 3. SET THIS to True to find the correct threshold, then False to run the merge.
DIAGNOSTIC_MODE = False

# 4. UPDATE THIS after running diagnostics. It must be larger than your small
#    pages but smaller than your large pages.
HEIGHT_THRESHOLD = 250 

# 5. (Optional) Adjust DPI for image quality. 150-200 is good for scans.
DPI = 150

# ---------------------

def process_pdf_scans(input_path, output_path, diagnostic_mode, height_threshold, dpi):
    """
    Extracts pages from a PDF, merges small artifact pages, and saves to a new PDF.
    Includes a diagnostic mode to help find the correct height threshold.
    """
    pdf_path = Path(input_path)
    if not pdf_path.is_file():
        print(f"❌ Error: File not found at '{input_path}'")
        return

    # 1. Extract all pages from the PDF into PIL Image objects
    print(f"🔍 Extracting pages from '{pdf_path.name}' at {dpi} DPI...")
    page_images = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            page_images.append(image)
        doc.close()
        print(f"✅ Extracted {len(page_images)} pages.")
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return

    # 2. Run Diagnostic Mode if enabled
    if diagnostic_mode:
        print("\n--- DIAGNOSTIC MODE ---")
        print("Analyzing page dimensions to help you set the right threshold...\n")
        for i, img in enumerate(page_images):
            print(f"Page {i + 1}: {img.width}x{img.height} pixels")
        print("\nBased on the dimensions above, find the height of your small 'artifact' pages.")
        print("Please update the HEIGHT_THRESHOLD value in the script to be slightly larger than that.")
        print("Then, set DIAGNOSTIC_MODE to False and run the script again.")
        return # Stop execution after diagnostics

    # 3. Group images for merging
    print("🧐 Grouping pages based on threshold...")
    page_groups = []
    for img in page_images:
        if img.height < height_threshold and page_groups:
            page_groups[-1].append(img)
        else:
            page_groups.append([img])

    # 4. Merge the images within groups
    print("✨ Processing and merging pages...")
    final_pages = []
    merged_count = 0
    for group in page_groups:
        if len(group) <= 1:
            final_pages.append(group[0])
            continue
        
        merged_count += (len(group) - 1)
        total_height = sum(img.height for img in group)
        max_width = max(img.width for img in group)
        final_image = Image.new('RGB', (max_width, total_height), 'white')
        
        current_y = 0
        for img in group:
            img_to_paste = img.convert('RGB')
            paste_x = (max_width - img_to_paste.width) // 2
            final_image.paste(img_to_paste, (paste_x, current_y))
            current_y += img_to_paste.height
        final_pages.append(final_image)

    if merged_count == 0:
        print("\n⚠️ No pages were merged. Your HEIGHT_THRESHOLD might still be too low.")
        print(f"   The smallest page found had a height greater than {height_threshold} pixels.")
        print("   Try running in Diagnostic Mode again if you're unsure.")
        return

    # 5. Save the processed pages into a new PDF file
    print(f"💾 Saving new PDF with {len(final_pages)} pages to '{output_path}'...")
    final_pages[0].save(
        output_path,
        save_all=True,
        append_images=final_pages[1:]
    )
    
    print("\n--------------------")
    print(f"🎉 All done! Merged {merged_count} artifact(s). Cleaned PDF saved successfully.")


if __name__ == "__main__":
    if INPUT_PDF == "path/to/your/manga.pdf":
         print("👉 Please edit the script and change the 'INPUT_PDF' variable.")
    else:
        process_pdf_scans(INPUT_PDF, OUTPUT_PDF, DIAGNOSTIC_MODE, HEIGHT_THRESHOLD, DPI)