import openai
import json
import numpy as np
import time


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

def generate_embeddings(json_file, output_file):
    # Load the JSON file
    with open(json_file, "r") as f:
        data = json.load(f)

    embeddings_list = []
    for file in data:
        for key in file:
            if key == "file":
                continue
            for i in file[key]:
                to_embed = file["file"] + i
                print(to_embed)
                time.sleep(0.025)
                embedding = get_embedding(to_embed)  # Replace this with your embedding function
                embeddings_list.append((embedding, to_embed))
                time.sleep(1)

    # Convert the list of pairs to a NumPy array
    embeddings_array = np.array(embeddings_list, dtype=object)

    # Save the NumPy array to a file
    np.save(output_file, embeddings_array)




# loaded_embeddings = np.load("embeddings.npy", allow_pickle=True)


if __name__ == "__main__":
    generate_embeddings("small/small_output_sections.json", "embeddings.npy")