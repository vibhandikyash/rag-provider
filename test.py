import openai
import os
from dotenv import load_dotenv

load_dotenv()


print(os.getenv("OPENAI_API_KEY"))
# Set API key
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Call the embeddings endpoint (updated)
# response = client.embeddings.create(
#     input="New hello world",
#     model="text-embedding-3-large"
# )

# embedding_vector = response.data[0].embedding

# with open("embedding.txt", "w") as f:
#     f.write(str(embedding_vector))