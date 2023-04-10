# Steps
1. Pre-process the code-repo/knowledge base (docs)
2. Store embeddings in a database 
3. Inject content into GPT-3 Prompt


# How SupaBase does it
1. Parsing the Supabase docs into sections.
2. Creating embeddings for each section using OpenAI's embeddings API.
3. Storing the embeddings in Postgres using the pgvector extension.
4. Getting a user's question.
5. Query the Postgres database for the most relevant documents related to the question.
6. Inject these documents as context for GPT-3 to reference in its answer.
7. Streaming the results back to the user in realtime.

# How we can do it
1. Parsing the PODPAC git repo into sections. **DONE**
2. Creating embeddings for each section using OpenAI's embeddings API. 
3. Storing the embeddings in Postgres using the pgvector extension.
4. Getting a user's question.
5. Query the Postgres database for the most relevant documents related to the question.
6. Inject these documents as context for GPT-3 to reference in its answer.
7. Streaming the results back to the user in realtime.

# Another Way
Use Retrievers!


## Presenting:

Block Diagrams

## Use Cases:
Input a python file, output:
1. Functions with docstrings
2. MD file for documentation.
3. Trace multi-file function calls (promise chains)

