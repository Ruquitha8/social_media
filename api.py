from fastapi import FastAPI
from llm_handler_simple import LLMHandler
from image_handler_simple import ImageHandler
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

llm = LLMHandler()
img = ImageHandler()


@app.get("/")
def home():
    return {"message": "API running"}


@app.post("/generate")
def generate(product_name: str, description: str, platform: str, tone: str, content_type: str, num_images: int = 1):

    
    result = llm.generate_post(
        product_name=product_name,
        product_description=description,
        platform=platform,
        tone=tone,
        content_type=content_type
    )

    
    image_paths = []

    if num_images > 0:
        images = img.generate_product_image(
            product_name=product_name,
            product_description=description,
            num_images=num_images
        )

        for i, image in enumerate(images):
            filename = f"generated_image_{i+1}.png"
            image.save(filename)
            image_paths.append(filename)

    return {
        "content": result,
        "images": image_paths
    }