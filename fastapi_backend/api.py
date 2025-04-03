from fastapi import FastAPI, HTTPException
from diffusers import StableDiffusionPipeline
from peft import PeftModel
import torch
from PIL import Image
from io import BytesIO
import base64

app = FastAPI()

# Load the model
base_model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    base_model_id,
    torch_dtype=torch.float16,
    use_safetensors=True
)
unet_base = pipe.unet
lora_model_id = "AryanMakadiya/pokemon_lora"
unet = PeftModel.from_pretrained(unet_base, lora_model_id)
pipe.unet = unet
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipe.to(device)

@app.post("/generate-image")
async def generate_image(prompt: str):
    try:
        with torch.autocast(device_type=device if device == "cuda" else "cpu"):
            image = pipe(
                prompt,
                num_inference_steps=50,
                guidance_scale=7.5
            ).images[0]

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {"image": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))