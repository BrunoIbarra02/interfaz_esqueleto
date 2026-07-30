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

def encode_text(model,tokenizer,texts):
    """
    Convierte uno o varios textos en embeddings con OpenCLIP
    
    Parametros
    ----------------
    
    model
        Modelo OpenCLIP
        
    tokenizer
        Tokenizer asociado al model
        
    texts : list[str]
        Lista de textos
    
    Retorna
    ----------------
    torch.Tensor
        Embeddings de los textos

    """
    device = next(model.parameters()).device
    
    tokens = tokenizer(texts).to(device)
    
    with torch.no_grad():
        embeddings = model.encode_text(tokens)
    
    return embeddings

import torch.nn.functional as F

def compute_similarity(image_embedding, text_embeddings):
    """
    Calcula la similitud entre una imagen y varios textos.


    Parametros
    -------------------

    image_embedding
        Embedding de una imagen.

    text_embeddings
        Embeddings de varios textos.


    Retorna
    -------------------

    torch.Tensor
        Vector con la similitud de la imagen respecto a cada texto.

    """

    image_embedding = F.normalize(image_embedding, dim=-1)
    text_embeddings = F.normalize(text_embeddings, dim=-1)

    similarity = image_embedding @ text_embeddings.T

    return similarity.squeeze(0)
    
    