from fastapi import FastAPI, HTTPException, Body
from diffusers import StableDiffusionPipeline
from peft import PeftModel
import torch
from PIL import Image
from io import BytesIO
import base64
from pydantic import BaseModel

# Define request model
class PromptRequest(BaseModel):
    prompt: str

app = FastAPI()

# Load the model
base_model_id = "runwayml/stable-diffusion-v1-5"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Use float32 for CPU, float16 for CUDA
dtype = torch.float16 if device == "cuda" else torch.float32

pipe = StableDiffusionPipeline.from_pretrained(
    base_model_id,
    torch_dtype=dtype,
    use_safetensors=True
)

unet_base = pipe.unet
lora_model_id = "AryanMakadiya/pokemon_lora"
unet = PeftModel.from_pretrained(unet_base, lora_model_id)
pipe.unet = unet
pipe = pipe.to(device)

@app.post("/generate-image")
async def generate_image(request: PromptRequest):
    try:
        if device == "cuda":
            with torch.autocast(device_type="cuda"):
                image = pipe(
                    request.prompt,
                    num_inference_steps=50,
                    guidance_scale=7.5
                ).images[0]
        else:
            # No autocast for CPU
            image = pipe(
                request.prompt,
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
