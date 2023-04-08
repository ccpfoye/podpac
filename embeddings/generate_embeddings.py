import openai


"""
    def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

    df['ada_embedding'] = df.combined.apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))
    df.to_csv('output/embedded_1k_reviews.csv', index=False)
"""

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def generate_embeddings(json_file):
    # Load the JSON file
    with open(json_file, "r") as f:
        data = json.load(f)

    # Extract the comments, docstrings, and code snippets
    comments = data["comments"]
    docstrings = data["docstrings"]
    code_snippets = data["code_snippets"]



    # Generate the embeddings for each comment, docstring, and code_snippet:
    comment_embeddings = []
    for comment in comments:
        comment_embeddings.append(get_embedding(comment))
    
    docstring_embeddings = []
    for docstring in docstrings:
        docstring_embeddings.append(get_embedding(docstring))
    
    code_snippet_embeddings = []
    for code_snippet in code_snippets:
        code_snippet_embeddings.append(get_embedding(code_snippet))
    