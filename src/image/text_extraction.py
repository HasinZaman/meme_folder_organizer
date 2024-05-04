from src.model_initialization import initialize
initialize()

from typing import Callable, Tuple, List

from multiprocessing import Process
from multiprocessing.connection import Connection

from PIL import Image

import numpy as np
import torch

from doctr.models import ocr_predictor
from doctr.models.predictor import OCRPredictor
from doctr.io import DocumentFile

from functional import seq

from src.util.async_model import model_loop

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    assume_straight_pages, straighten_pages, bin_thresh = True, False, 0.3
    model = ocr_predictor(
        "db_resnet50",
        "crnn_vgg16_bn",
        pretrained=True,
        assume_straight_pages=assume_straight_pages,
        straighten_pages=straighten_pages,
        export_as_straight_boxes=straighten_pages,
        detect_orientation=not assume_straight_pages,
    ).to(device)
    model.det_predictor.model.postprocessor.bin_thresh = bin_thresh


    def eval(image_path: str) -> str:
        img = DocumentFile.from_images(image_path)[0]

        content = model([img])

        all_lines: List[List[str]] = []

        for block in content.pages[0].blocks:
            line_tmp = " ".join(seq(block.lines)
                .map(lambda line:  " ".join(seq(line.words)
                    .map(lambda word: word.value)
                    .list()
                ))
                .list()
            )

            average_block_confidence = (seq(block.lines)
                .map(lambda line: seq(line.words)
                    .map(lambda word: word.confidence)
                    .average()
                )
                .average()
            )
            
            if average_block_confidence > 0.6:
                all_lines.append(line_tmp)

        return (image_path, all_lines)
    return eval

text_extraction_worker: Callable[[], Tuple[Connection, Connection, Process]] = model_loop(load_model)