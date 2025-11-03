import urllib.request
import urllib.parse
import ssl
import re
import os
from html.parser import HTMLParser
import trafilatura

class ArxivSearchParser(HTMLParser):
    """Parser to extract arXiv paper IDs from search results."""
    
    def __init__(self):
        super().__init__()
        self.paper_ids = []
        self.current_link = None
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            # Look for links to arXiv papers (format: /abs/XXXX.XXXXX)
            if '/abs/' in href:
                match = re.search(r'/abs/(\d+\.\d+)', href)
                if match:
                    paper_id = match.group(1)
                    if paper_id not in self.paper_ids:
                        self.paper_ids.append(paper_id)


_context = ssl._create_unverified_context()


def fetch_paper_ids(url, max_pages=1):
    """
    Fetch search results from arXiv and extract paper IDs.
    
    Args:
        url: The search URL
        max_pages: Number of pages to fetch (default: 1)
    
    Returns:
        List of paper IDs
    """
    all_paper_ids = []
    
    for page in range(max_pages):
        # Add pagination parameter
        if page > 0:
            if '?' in url:
                page_url = f"{url}&start={page * 200}"
            else:
                page_url = f"{url}?start={page * 200}"
        else:
            page_url = url
        
        print(f"Fetching page {page + 1}...")
        
        try:
            # Set a user agent to avoid being blocked
            req = urllib.request.Request(
                page_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            with urllib.request.urlopen(req, context=_context) as response:
                html = response.read().decode('utf-8')
            
            # Parse the HTML to extract paper IDs
            parser = ArxivSearchParser()
            parser.feed(html)
            
            paper_ids = parser.paper_ids
            all_paper_ids.extend(paper_ids)
            
            print(f"Found {len(paper_ids)} papers on page {page + 1}")
            
            # Be polite - wait between requests
            if page < max_pages - 1:
                time.sleep(3)
        
        except Exception as e:
            print(f"Error fetching page {page + 1}: {e}")
            break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ids = []
    for pid in all_paper_ids:
        if pid not in seen:
            seen.add(pid)
            unique_ids.append(pid)
    
    return unique_ids


def download_pdf(paper_id, output_dir='arxiv_pdfs'):
    """
    Download a PDF file from arXiv.
    
    Args:
        paper_id: The arXiv paper ID (e.g., '2301.12345')
        output_dir: Directory to save PDFs
    
    Returns:
        True if successful, False otherwise
    """
    
    # Construct PDF URL
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    
    # Construct filename (sanitize paper_id for filesystem)
    filename = f"{paper_id.replace('/', '_')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"  ✓ Already exists: {filename}")
        return True
    
    try:
        print(f"  Downloading: {filename}...", end=' ')
        
        # Set user agent
        req = urllib.request.Request(
            pdf_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        # Download the PDF
        with urllib.request.urlopen(req, context=_context) as response:
            pdf_data = response.read()
        
        # Save to file
        with open(filepath, 'wb') as f:
            f.write(pdf_data)
        
        # Get file size
        size_mb = len(pdf_data) / (1024 * 1024)
        print(f"✓ Done ({size_mb:.2f} MB)")
        return True
    
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def clean_web_content(page_url):
    downloaded_html = trafilatura.fetch_url(page_url)

    cleaned_text = trafilatura.extract(
        downloaded_html,
        include_comments=False,
        include_tables=False,
        deduplicate=True
    )

    return cleaned_text
    


def generate_clean_json(arxiv_ids, content):
    
    """
    Parse the content cleaned by trafilatura containing arxiv paper information.
    Each paper is delimited by a single '-' line.
    Since the arxiv id information was eliminated in the content, an extra arxiv_ids is passed for generating url field
    """
    
    # Split by delimiter (single '-' on its own line)
    papers_raw = content.split('-\n')
    
    papers = []
    index = 0
    
    for paper_text in papers_raw:
        paper_text = paper_text.strip()
        if not paper_text or paper_text == '-':
            continue
        
        lines = paper_text.split('\n')
        
        paper = {
            'url': '',
            'title': '',
            'authors': [],
            'abstract': '',
            'date': ''
        }
        
        # Find key sections
        authors_idx = -1
        abstract_idx = -1
        more_idx = -1
        less_idx = -1
        
        for i, line in enumerate(lines):
            if line.strip() == 'Authors:':
                authors_idx = i
            elif line.strip() == 'Abstract:':
                abstract_idx = i
            elif '▽ More' in line:
                more_idx = i
            elif '△ Less' in line:
                less_idx = i
        
        # Extract title (first line)
        if lines:
            paper['title'] = lines[0].strip()
        
        # Extract authors (between 'Authors:' and 'Abstract:')
        if authors_idx != -1 and abstract_idx != -1:
            author_lines = lines[authors_idx + 1:abstract_idx]
            authors = []
            for line in author_lines:
                line = line.strip()
                if line and line != 'Authors:':
                    # Remove trailing comma if present
                    author = line.rstrip(',').strip()
                    if author:
                        authors.append(author)
            paper['authors'] = authors
        
        # Extract abstract (between '▽ More' and '△ Less',  or between 'Abstract:' and '△ Less')
        if more_idx != -1 and less_idx != -1:
            abstract_lines = lines[more_idx + 1:less_idx]
            paper['abstract'] = ' '.join(line.strip() for line in abstract_lines if line.strip())
        elif abstract_idx != -1 and less_idx != -1:
            abstract_lines = lines[abstract_idx + 1:less_idx]
            paper['abstract'] = ' '.join(line.strip() for line in abstract_lines if line.strip())
        
        # Extract date (line with format 'Submitted xxx;')
        for line in lines:
            # Extract the date part
            match = re.search(r'Submitted (.+);', line.strip())
            if match:
                submit_date = match.group(1)
                paper['date'] = submit_date
                break

        # Construct url:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_ids[index]}.pdf"
        paper['url'] = pdf_url
        index += 1

        # Only add paper if it has at least a title
        if paper['title']:
            papers.append(paper)
    
    return papers
