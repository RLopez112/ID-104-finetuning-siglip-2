"""SigLIP 2 Vision-Language Inference Service."""
from typing import List, Optional, Union
import numpy as np
from PIL import Image
import torch
from transformers import AutoModel, AutoProcessor

from .config import DEFAULT_MODEL_NAME


class SigLIP2Service:
    """Encodes text queries and 2D images into normalized L2 unit vectors using SigLIP 2."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        torch_dtype: Optional[torch.dtype] = None,
    ):
        self.model_name = model_name

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        if torch_dtype is None:
            self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        else:
            self.dtype = torch_dtype

        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(
            self.model_name,
            dtype=self.dtype,
        ).to(self.device)
        self.model.eval()

    @torch.no_grad()
    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Encodes text queries into normalized L2 float32 vectors.
        Applies standard prompt prefix ('a photo of a ...') and padding='max_length'
        mandated by SigLIP architecture.
        """
        if isinstance(text, str):
            text = [text]

        # Apply prompt template if not already present
        templated = []
        for t in text:
            t_clean = t.strip()
            if not t_clean.lower().startswith("a photo of") and not t_clean.lower().startswith("a 3d model of"):
                templated.append(f"a photo of a {t_clean}")
            else:
                templated.append(t_clean)

        inputs = self.processor(
            text=templated,
            padding="max_length",
            return_tensors="pt",
        ).to(self.device)

        output = self.model.get_text_features(**inputs)

        # Extract pooled feature tensor from BaseModelOutputWithPooling or raw Tensor
        text_features = output.pooler_output if hasattr(output, "pooler_output") else output
        
        # L2 Normalization for Cosine Similarity
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        return text_features.cpu().to(torch.float32).numpy()

    @torch.no_grad()
    def encode_image(self, images: Union[Image.Image, List[Image.Image]]) -> np.ndarray:
        """
        Encodes one or more PIL images into normalized L2 float32 vectors.
        """
        if isinstance(images, Image.Image):
            images = [images]

        # Convert to RGB to handle PNG RGBA transparency correctly
        rgb_images = [img.convert("RGB") if img.mode != "RGB" else img for img in images]

        inputs = self.processor(images=rgb_images, return_tensors="pt").to(self.device)
        if self.dtype == torch.float16 and "pixel_values" in inputs:
            inputs["pixel_values"] = inputs["pixel_values"].to(torch.float16)

        output = self.model.get_image_features(**inputs)

        # Extract pooled feature tensor from BaseModelOutputWithPooling or raw Tensor
        image_features = output.pooler_output if hasattr(output, "pooler_output") else output

        # L2 Normalization for Cosine Similarity
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        return image_features.cpu().to(torch.float32).numpy()

    def encode_image_path(self, image_path: str) -> np.ndarray:
        with Image.open(image_path) as img:
            return self.encode_image(img)
