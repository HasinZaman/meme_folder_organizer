from src.model_initialization import initialize
initialize()

from typing import Tuple, Callable, List

from multiprocessing import Process
from multiprocessing.connection import Connection

from PIL import Image

import numpy as np

from sentence_transformers import SentenceTransformer, util
import torch

from src.util.async_model import model_loop
from src.util.input_wrapper import Img, Text

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer("clip-ViT-B-32", device=device)

    def eval(input_val: Img | Text) -> Tuple[Img | Text, List[float]]:
        embedding = []
        match input_val:
            case Img(image_path):
                img: Image = Image.open(image_path)

                embedding = model.encode(img)
            case Text(text):
                embedding = model.encode(text)

        return (input_val, embedding.tolist())
    return eval

embedding_worker: Callable[[], Tuple[Connection, Connection, Process]] = model_loop(load_model)
