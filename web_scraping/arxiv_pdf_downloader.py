import util
import time
import os
from pathlib import Path

def main():
    # The search URL
    search_url = "https://arxiv.org/search/advanced?advanced=1&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-physics=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=past_12&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first"
    
    # Output directory for PDFs
    output_dir = 'arxiv_pdfs'
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("ArXiv PDF Downloader")
    print("="*80)
    print(f"\nSearch URL: {search_url}")
    print(f"Output directory: {output_dir}\n")
    
    # Fetch paper IDs from search results
    print("Step 1: Fetching search results...")
    paper_ids = util.fetch_paper_ids(search_url, max_pages=1)
    
    if not paper_ids:
        print("No papers found!")
        return
    
    print(f"\nFound {len(paper_ids)} unique papers total\n")
    
    # Download PDFs
    print("Step 2: Downloading PDFs...")
    print("-"*80)
    
    successful = 0
    failed = 0
    
    for i, paper_id in enumerate(paper_ids, 1):
        print(f"[{i}/{len(paper_ids)}] {paper_id}")
        
        if util.download_pdf(paper_id, output_dir):
            successful += 1
        else:
            failed += 1
        
        # Be polite - wait between downloads
        if i < len(paper_ids):
            time.sleep(3)
    
    # Summary
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80)
    print(f"Total papers: {len(paper_ids)}")
    print(f"Successful downloads: {successful}")
    print(f"Failed downloads: {failed}")
    print(f"PDFs saved to: {os.path.abspath(output_dir)}")
    print("="*80)

if __name__ == "__main__":
    main()