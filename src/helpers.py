# CONTAINS HELPER FUNCTIONS
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
import torch
from PIL import Image
from io import BytesIO
from fastapi import UploadFile
import pillow_avif


def get_model_info():
    # Set the device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Define the model ID
    model_ID = "openai/clip-vit-base-patch32"

    # Save the model to device
    clip_model = CLIPModel.from_pretrained(model_ID).to(device)

    # Get the processor
    clip_processor = CLIPProcessor.from_pretrained(model_ID)

    # Get the tokenizer
    clip_tokenizer = CLIPTokenizer.from_pretrained(model_ID)

    # Return model, processor & tokenizer
    return clip_model, clip_processor, clip_tokenizer, device

def get_single_image_embedding(product_image, processor, model, device):
  image = processor(
      text = None,
      images = product_image,
      return_tensors="pt"
      )["pixel_values"].to(device)
  embedding = model.get_image_features(image)
  # convert the embeddings to numpy array
  return embedding.cpu().detach().numpy().flatten().tolist()

async def get_image(image: UploadFile):
    try:
        image_data = await image.read()
        image = Image.open(BytesIO(image_data)).convert("RGB")
        return image
    except Exception as e:
        # Handle specific exceptions or log the error
        print(f"Error loading image: {e}")
        return None  # Or raise an error as needed