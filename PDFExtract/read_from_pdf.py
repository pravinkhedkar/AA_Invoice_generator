import pdfplumber
from time import time
import os

pdf_path = "C:\\Users\\DELL\\Downloads\\SK_Pdf_Personal.pdf"
output_dir = "extracted_pages"

try:
    start = time()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages in PDF: {total_pages}")
        print("=" * 80)
        
        # Iterate through all pages
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            
            # Create output filename for each page
            output_file = os.path.join(output_dir, f"page_{page_num:03d}.txt")
            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text if text else "[Empty page - no text found]")
            
            print(f"✓ Page {page_num:03d} saved to: {output_file}")
            print(f"  Text length: {len(text) if text else 0} characters")
        
        print("=" * 80)
        print(f"\n✓ All pages successfully extracted to: {output_dir}")
    
    end = time()
    print(f"Time taken: {end - start:.2f} seconds")
        
except FileNotFoundError:
    print(f"Error: PDF file not found at {pdf_path}")
except Exception as e:
    print(f"Error reading PDF: {e}")