from src.model_initialization import initialize
initialize()

from typing import Tuple, Callable

from multiprocessing import Process
from multiprocessing.connection import Connection

from PIL import Image

from transformers import Blip2Processor, Blip2ForConditionalGeneration, AutoConfig
import torch

from src.util.async_model import model_loop

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = Blip2Processor.from_pretrained(
        f"Salesforce/blip2-opt-2.7b",
    )
    #"Salesforce/blip2-opt-2.7b",#
    model = Blip2ForConditionalGeneration.from_pretrained(
        f"Salesforce/blip2-opt-2.7b",
        load_in_8bit=True,
        device_map=device,
        torch_dtype=torch.float16,
    )

    def eval(image_path: str) -> str:
        img: Image = Image.open(image_path)

        inputs = processor(images=img, return_tensors="pt").to(device)

        generated_ids = model.generate(**inputs)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

        return generated_text
    return eval

caption_worker: Callable[[], Tuple[Connection, Connection, Process]] = model_loop(load_model)
