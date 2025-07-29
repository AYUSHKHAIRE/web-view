import gc
import torch
from PIL import Image
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoModelForImageTextToText,
    GenerationConfig
)

# Step 1: Clear memory
gc.collect()
torch.cuda.empty_cache()
torch.cuda.ipc_collect()

# Step 2: Paths and dtype
model_path = "/home/ayushkhaire/code/accessweb/web-view/accessweb/browse/models/gemma-3n-transformers-gemma-3n-e2b-it-v1"
dtype = torch.bfloat16  # fallback to torch.float16 if bfloat16 fails

# ==== TEXT GENERATION ====

# Step 3a: Load tokenizer and text model
text_tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
text_model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=dtype, device_map="auto")

# Step 4a: Run text-only inference
prompt = "What is the capital of France?"
inputs = text_tokenizer(prompt, return_tensors="pt").to(text_model.device)
generation_config = GenerationConfig(max_new_tokens=50, do_sample=False)
outputs = text_model.generate(**inputs, generation_config=generation_config)
result = text_tokenizer.decode(outputs[0], skip_special_tokens=True)
print("💬 Text Answer:")
print(result)

# ==== IMAGE + TEXT MULTIMODAL ====

# Step 3b: Load processor and multimodal model
image_model = AutoModelForImageTextToText.from_pretrained(model_path, torch_dtype=dtype, device_map="auto")
processor = AutoProcessor.from_pretrained(model_path)

# Step 4b: Load local image
image_path = "/home/ayushkhaire/code/accessweb/web-view/assets/code/Screenshot from 2025-03-16 21-28-15.png"
image = Image.open(image_path)

# Step 5b: Create multimodal input
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": "What is in this image?"}
        ]
    }
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt"
).to(image_model.device, dtype=image_model.dtype)
input_len = inputs["input_ids"].shape[-1]

# Step 6b: Generate output
outputs = image_model.generate(**inputs, max_new_tokens=512, disable_compile=True)
response = processor.batch_decode(outputs[:, input_len:], skip_special_tokens=True)[0]

print("\n🖼️ Image + Text Answer:")
print(response)
