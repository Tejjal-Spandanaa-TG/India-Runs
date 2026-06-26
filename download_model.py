import os
from sentence_transformers import SentenceTransformer

def main():
    model_name = "all-MiniLM-L6-v2"
    local_dir = os.path.join(os.path.dirname(__file__), "embedding_model")
    print(f"Downloading model '{model_name}'...")
    
    # Force downloads and save to the local path
    model = SentenceTransformer(model_name)
    model.save(local_dir)
    print(f"Model saved successfully to '{local_dir}'")

if __name__ == "__main__":
    main()
