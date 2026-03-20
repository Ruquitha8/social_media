import requests
from typing import List
from PIL import Image
from io import BytesIO
from config_simple import HF_API_KEY, IMAGE_MODEL, IMAGE_TIMEOUT


class ImageHandler:
    def __init__(self):
        if not HF_API_KEY:
            raise Exception("HF_API_KEY missing")

        # Updated router endpoint
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{IMAGE_MODEL}"

        self.headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
        }

    def generate_product_image(
        self,
        product_name: str,
        product_description: str,
        num_images: int = 1,
    ) -> List[Image.Image]:

        prompt = f"{product_name}. {product_description}. High quality, professional product photography"

        images = []

        for _ in range(num_images):

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt},
                timeout=IMAGE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(response.text)

            # Router sometimes returns JSON with base64
            try:
                result = response.json()
                if isinstance(result, dict) and "error" in result:
                    raise Exception(result["error"])
            except Exception:
                pass

            image = Image.open(BytesIO(response.content)).convert("RGB")
            images.append(image)

        return images 