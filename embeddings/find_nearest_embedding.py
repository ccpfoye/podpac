import numpy as np
# import a kd-tree
from generate_embeddings import get_embedding
from scipy.spatial import cKDTree
import openai
import re

def clean_string(text):
    # Remove \n characters
    text = text.replace('\n', ' ')

    # Remove '>>>' characters
    text = text.replace('>>>', '')

    # Remove multiple consecutive spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text


def find_nearest_embeddings(tree, embedding, loaded_embeddings, k=5):
    # Find the k nearest embeddings
    dist, idx = tree.query(embedding, k=k)
    return dist, loaded_embeddings[idx, 1]

if __name__ == "__main__":
    # Load the embeddings
    sys_message = 'You are a very enthusiastic PDOPAC representative who loves to help people! Given the following sections from the PODPAC documentation or python code, using that information to inform your answer which is outputted in markdown format. If the the information is from documentation, it will start with "HOW TO <doc title>", if it is from the code, it will start with "FROM <python filename> - <class name> - <function name>".'
    code_embeddings_file = "code/code_embeddings.npy"
    doc_embeddings_file = "docs/doc_embeddings.npy"
    
    loaded_embeddings_code = np.load(code_embeddings_file, allow_pickle=True)
    embeddings_code = loaded_embeddings_code[:, 0]
    code_embeddings_array = np.stack(embeddings_code, axis=0)
    
    loaded_embeddings_doc = np.load(doc_embeddings_file, allow_pickle=True)
    embeddings_doc = loaded_embeddings_doc[:, 0]
    doc_embeddings_array = np.stack(embeddings_doc, axis=0)
    
    code_and_doc_embeddings = np.concatenate((code_embeddings_array, doc_embeddings_array), axis=0)
    loaded_embeddings = np.concatenate((loaded_embeddings_code, loaded_embeddings_doc), axis=0)
    
    # Create a kd-tree
    tree = cKDTree(code_and_doc_embeddings)
    # Find the nearest embeddings
    while True:
        # Get string from user:
        text = input("Enter a string to find similar strings: ")
        embedding = get_embedding(text)
        dist, nearest_embeddings = find_nearest_embeddings(tree, embedding, loaded_embeddings, k=15)
        print(dist)
        print(nearest_embeddings)
        content_sections = "CONTENT SECTIONS: " + clean_string(str(nearest_embeddings))
        question = "QUESTION: " + text
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_message},
                {"role": "user", "content": content_sections + "\n" + question}
            ]
        )
        
        print(completion.choices[0].message)




