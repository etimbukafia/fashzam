# CONTAINS HELPER FUNCTIONS
import torch
from torchvision import transforms
from PIL import Image
from io import BytesIO
from fastapi import UploadFile
import pillow_avif


def get_model_info():
    dino_model = torch.hub.load('facebookresearch/dino:main', 'dino_vitb16', pretrained=True)

    # Set the device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dino_model = dino_model.to(device)

    dino_model.eval()

    # Return model, processor & tokenizer
    return dino_model, device

def process_images_For_dino():
  preprocess = transforms.Compose([
      transforms.Resize(224),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
  ])

  return preprocess

def get_single_dino_image_embedding(product_image, model, device):
  preprocess = process_images_For_dino()
  img_tensor = preprocess(product_image).unsqueeze(0).to(device)

  # Get the embedding without computing gradients
  with torch.no_grad():
    embedding = model(img_tensor)
    embedding = embedding.cpu().detach().numpy().flatten().tolist()

  return embedding

async def get_image(image: UploadFile):
    try:
        image_data = await image.read()
        image = Image.open(BytesIO(image_data)).convert("RGB")
        return image
    except Exception as e:
        # Handle specific exceptions or log the error
        print(f"Error loading image: {e}")
        return None  # Or raise an error as needed