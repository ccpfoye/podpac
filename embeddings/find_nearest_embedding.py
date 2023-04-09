import numpy as np
# import a kd-tree
from scipy.spatial import cKDTree

loaded_embeddings = np.load("small/embeddings_small.npy", allow_pickle=True)

embeddings = loaded_embeddings[:, 0]
embeddings_array = np.stack(embeddings, axis=0)
# Create a kd-tre
tree = cKDTree(embeddings_array)


def find_nearest_embeddings(tree, embedding, k=5, loaded_embeddings=loaded_embeddings):
    # Find the k nearest embeddings
    dist, idx = tree.query(embedding, k=k)
    return dist, loaded_embeddings[idx, 1]



