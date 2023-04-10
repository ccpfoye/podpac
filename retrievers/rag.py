from datasets import load_from_disk

# Replace the paths below with the paths to your saved dataset and index files
dataset_path = "/home/cfoye/Personal/podpac/retrievers/my_knowledge_dataset"
index_path = "/home/cfoye/Personal/podpac/retrievers/my_knowledge_dataset_hnsw_index.faiss"

# Load the dataset from disk
dataset = load_from_disk(dataset_path)

# Load the FAISS index
dataset.load_faiss_index("embeddings", index_path)

from transformers import AutoTokenizer, RagRetriever, RagModel, RagConfig
import torch

tokenizer = AutoTokenizer.from_pretrained("facebook/rag-token-nq")
from transformers import AutoConfig


retriever = RagRetriever.from_pretrained("facebook/rag-sequence-nq", indexed_dataset=dataset) 

model = RagModel.from_pretrained("facebook/rag-sequence-nq", retriever=retriever)
inputs = tokenizer("What is PODPAC?", return_tensors="pt")
outputs = model.generate(input_ids=inputs["input_ids"])
print(tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]) 