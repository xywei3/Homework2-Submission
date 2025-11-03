from datasketch import MinHash, MinHashLSH
import json

NUM_PERM = 128 # The number of permutations (hash functions)
SIMILARITY_THRESHOLD = 0.7
total_tokens = 0
removed_tokens = 0

def create_minhash(ngrams):
    m = MinHash(num_perm=NUM_PERM)
    for d in ngrams:
        m.update(d.encode('utf8'))
    return m


def create_ngrams(text, n=5, tokenizer='words'):
    if tokenizer == 'words':
        # Split into words and use as the set elements
        tokens = text.lower().split()
    elif tokenizer == 'ngrams':
        # Create character n-grams (shingles)
        tokens = [text[i:i+n] for i in range(len(text) - n + 1)]
    else:
        raise ValueError("Tokenizer must be 'words' or 'ngrams'")
        
    return set(tokens)


def deduplicate_text(sentences):
    # Initialize LSH index
    lsh = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=NUM_PERM)

    unique_sentences = {}
    
    # Store MinHashes in LSH
    for s_id, sentence in enumerate(sentences):
        ngrams = create_ngrams(sentence, n=5, tokenizer='words') # Using word n-grams here
        global total_tokens
        total_tokens += len(ngrams)
        minhash = create_minhash(ngrams)
        
        # Query LSH for existing near-duplicates
        result = lsh.query(minhash)
        
        # If no near-duplicates found, add to unique set and LSH index
        if not result:
            unique_sentences[s_id] = sentence
            lsh.insert(s_id, minhash) # Insert the unique sentence's MinHash
        else:
            global removed_tokens
            removed_tokens += len(sentence.split())

    return list(unique_sentences.values())


def main():
    print("Processing arxiv data...")
    with open('dataset/arxiv_clean.json', 'r') as file:
        data = json.load(file)
        for paper in data: 
            sentences = paper['abstract'].split('.')
            clean_abstract = deduplicate_text(sentences)
            paper['abstract'] = '.'.join(clean_abstract)
            
        print('Writing clean arxiv data into clean_corpous.txt...')
        with open('clean_corpus.txt', 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    print("Processing transcripts data...")
    
    with open('dataset/talks_transcripts.jsonl', 'r', encoding='utf-8') as f:
        transcripts = [line.strip() for line in f if line.strip()]
        transcripts_json = []
        for transcript_str in transcripts:
            transcript_json = json.loads(transcript_str)
            sentences = transcript_json['audio_text'].split('.')
            clean_audio_text = deduplicate_text(sentences)
            transcript_json['audio_text'] = '.'.join(clean_audio_text)
            transcripts_json.append(transcript_json)

        print('Writing clean transcripts data into clean_corpous.txt...')
        with open('clean_corpus.txt', 'a') as f:
            f.write('\n')
            for transcript in transcripts_json:
                f.write(json.dumps(transcript) + '\n')

    with open('stats.md', 'w') as f:
        f.write(f'token count: {total_tokens}\nremoval percentage: {removed_tokens*100/total_tokens}%')

if __name__ == "__main__":
    main()
