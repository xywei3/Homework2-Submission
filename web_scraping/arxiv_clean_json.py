import json
import util

def main():
    url = "https://arxiv.org/search/advanced?advanced=1&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-physics=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=past_12&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first"
    
    output_file = 'arxiv_clean.json'

    paper_ids = util.fetch_paper_ids(url)

    cleaned_text = util.clean_web_content(url)
    # write the clean web content to a file for reference
    with open('clean_web_content.txt', 'w') as f:
        f.write(cleaned_text)

    papers = util.generate_clean_json(paper_ids, cleaned_text)
    
    print(f"Found {len(papers)} papers")
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved to {output_file}")
    

if __name__ == "__main__":
    main()
