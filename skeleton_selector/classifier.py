"""
classifier.py
=============

Responsabilidad
---------------
Carga el modelo OpenCLIP y prepara los recursos necesarios para realizar
clasificación de imágenes.

Entradas
--------
Ninguna.

Salidas
-------
- Modelo OpenCLIP.
- Función de preprocesado de imágenes.
- Tokenizer asociado al modelo.

Dependencias
------------
- torch
- open_clip

No hace
--------
- No clasifica imágenes.
- No selecciona esqueletos.
- No contiene lógica de negocio.
"""

import open_clip
import torch

def load_model():
    """
    Carga el modelo OpenCLIP.

    Returns
    -------
    tuple
        (model, preprocess, tokenizer)
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained="laion2b_s34b_b79k",
        device=device,
    )

    tokenizer = open_clip.get_tokenizer("ViT-B-32")

    return model, preprocess, tokenizer

from PIL import Image

def encode_image(model,preprocess,image_path):
    """
    Convertimos la imagen en su embedding con OpenCLIP
    
    Parametros
    ----------------
    
    model
        Modelo OpenCLIP.
    
    preprocess
        Transformaciones necesarias para preparar la imagen.
        
    image_path : str
        Ruta de la imagen
        
    Retorna
    -----------------
    torch.Tensor
        Embedding de la imagen.
     
        
    """
    
    imagen = Image.open(image_path).convert("RGB")
    imagen = preprocess(imagen).unsqueeze(0)
    device = next(model.parameters()).device
    
    imagen = imagen.to(device)
    
    with torch.no_grad():
        embedding = model.encode_image(imagen)
        
    return embedding
    