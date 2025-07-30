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
from browse.logger_config import logger

class GemmaManager:
    def __init__(self):
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        self.model_path = "/home/ayushkhaire/code/accessweb/web-view/accessweb/browse/models/gemma-3n-transformers-gemma-3n-e2b-it-v1"
        self.dtype = torch.bfloat16 

    def setup(self):
        self.text_tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.text_model = AutoModelForCausalLM.from_pretrained(self.model_path, torch_dtype=self.dtype, device_map="auto")
        self.image_model = AutoModelForImageTextToText.from_pretrained(self.model_path, torch_dtype=self.dtype, device_map="auto")
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        logger.debug("[ GEMMA 3N ] Gemma setup complete successfully .")

    def ask_query(self, prompt):
        logger.debug(f"[ GEMMA 3N ] Received text prompt: {prompt}")
        inputs = self.text_tokenizer(prompt, return_tensors="pt").to(self.text_model.device)
        generation_config = GenerationConfig(
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        logger.debug(f"[ GEMMA 3N ] generating Response ..." )
        outputs = self.text_model.generate(**inputs, generation_config=generation_config)
        response = self.text_tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True
        )
        logger.debug(f"[ GEMMA 3N ] Response: {response}")
        return response

    def query_image(self,image_path , prompt):
        image = Image.open(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "What is in this image?"}
                ]
            }
        ]
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.image_model.device, dtype=self.image_model.dtype)
        input_len = inputs["input_ids"].shape[-1]
        outputs = self.image_model.generate(**inputs, max_new_tokens=512, disable_compile=True)
        response = self.processor.batch_decode(outputs[:, input_len:], skip_special_tokens=True)[0]
        logger.debug(f"[ GEMMA 3N ] Gemma got IMG prompt {prompt}")
        return response