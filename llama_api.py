from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

app = Flask(__name__)

try:
    print("Loading tokenizer...")
    model_path = "./llama_local"
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    print("Tokenizer loaded.")

    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)
    print("Model loaded.")

    print("Creating text generation pipeline...")
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")
    print("Pipeline ready.")
except Exception as e:
    print(f"Error during model setup: {e}")
    raise

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    output = generator(prompt, max_new_tokens=300, do_sample=True, truncation=True)
    return jsonify({"reply": output[0]["generated_text"]})

if __name__ == "__main__":
    print("Starting Flask server on http://localhost:5000")
    app.run(port=5000, debug=True)
