import os
import json
import requests
import threading
from PIL import Image
from io import BytesIO
from ComfyUI_IPAdapter_plus.utils import image_to_tensor
from ComfyUI_IPAdapter_plus.IPAdapterPlus import ipadapter_execute

class IPAdapterSameEnergy:
    """
    A ComfyUI node that fetches reference images from same.energy API and applies IPAdapter styling
    """
    def __init__(self):
        self.lock = threading.Lock()
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "ipadapter": ("IPADAPTER",),
                "clip_vision": ("CLIP_VISION",),
                "style_prompt": ("STRING", {
                    "multiline": False,
                    "default": "studio ghibli style"
                }),
                "weight": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 5.0,
                    "step": 0.01
                }),
                "start_at": ("FLOAT", { 
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001 
                }),
                "end_at": ("FLOAT", { 
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001 
                }),
            },
            "optional": {
                "image_negative": ("IMAGE",),
                "attn_mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply_style"
    CATEGORY = "ipadapter"

    def fetch_reference_image(self, text):
        """
        Fetches a reference image from same.energy based on the style prompt
        Returns: PIL Image object or None if fetch fails
        """
        # Query the API with quality keywords added
        results = requests.get(f"https://imageapi.same.energy/search?text=art masterpiece best quality {text}&n=100")
        
        if results.status_code == 200:
            if len(results.text.splitlines()) > 1:
                # This result was not cached
                try:
                    results = json.loads(results.text.splitlines()[2])
                except:
                    # Handle API error case where a word isn't recognized
                    results = json.loads(results.text.splitlines()[1])
                    split_1 = results["message"].split("The word '")[1]
                    word = split_1.split("' isn't recognized")[0]
                    # Recursively try again without the problematic word
                    return self.fetch_reference_image(text.replace(word, ""))
            else:
                # This result was cached
                results = results.json()

        # Get first valid result
        if results and 'payload' in results and 'images' in results['payload']:
            result = results['payload']['images'][0]
            # https://blobcdn.same.energy/thumbnails/blobs/b/85/d1/85d18f3edbda90f75a2678cb33ef0206f39f3a57
            
            # {"id": "yPnSx", "sha1": "dc16001f7e9aa0a61c61b0ae0437f2d868c07a2a", "prefix": "a", "width": 512, "height": 723, "metadata": {"source": "pinterest", "caption": null, "title": "anime: totoro", "nsfw": false, "post_url": "https://www.pinterest.com/pin/445786063091498852/", "original_url": "http://matome.naver.jp/odai/2134250139839101201/2134252791441298003", "tags": {}}}
            # https://blobcdn.same.energy/thumbnails/blobs/a/dc/16/dc16001f7e9aa0a61c61b0ae0437f2d868c07a2a
            
            sha1 = result['sha1']
            prefix = result['prefix']
            # Construct URL for full image
            url = f"https://blobcdn.same.energy/{prefix}/{sha1[:2]}/{sha1[2:4]}/{sha1}"
            
            response = requests.get(url)
            # Create an in-memory image from the downloaded bytes
                # img = Image.open(BytesIO(request.content))
                # Check if both dimensions are at least 512x512
                # if img.width >= 512 and img.height >= 512:
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        return None

    def apply_style(self, model, ipadapter, clip_vision, style_prompt, weight, start_at=0.0, end_at=1.0, image_negative=None, attn_mask=None):
        # Fetch reference image based on style prompt
        reference_img = self.fetch_reference_image(style_prompt)
        
        if reference_img is None:
            raise ValueError("Could not fetch valid reference image")

        # Convert PIL image to tensor format
        image = image_to_tensor(reference_img)
        
        # Call IPAdapter execute function with our parameters
        model = ipadapter_execute(
            model=model,
            ipadapter=ipadapter,
            clipvision=clip_vision,
            image=image,
            image_negative=image_negative,
            weight=weight,
            start_at=start_at,
            end_at=end_at,
            attn_mask=attn_mask
        )
        
        # Cleanup reference image
        reference_img.close()
        
        return (model,)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "IPAdapterSameEnergy": IPAdapterSameEnergy
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IPAdapterSameEnergy": "IPAdapter (Same.Energy)"
}
