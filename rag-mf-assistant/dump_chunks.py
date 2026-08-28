import json
from ingestion.chunker import chunk_all_documents

def main():
    chunks = chunk_all_documents()
    with open('chunks_preview.json', 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"Dumped {len(chunks)} chunks to chunks_preview.json")

if __name__ == '__main__':
    main()
