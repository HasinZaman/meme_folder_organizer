from typing import List, Tuple, Set
import os

from threading import Thread

from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection

from functional import seq

from src.util.input_wrapper import Img, Video

IMG_EXT: Set[str] = set(["png", "jpg", "jpeg"])
VIDEO_EXT: Set[str] = set(["mp4", "avi", "mov"])

def all_files(*root_dirs: str) -> Tuple[Thread, Connection]:
    output_recv, output_sender = Pipe(duplex=False)

    workers: List[Tuple[Process, Connection]] = (seq(root_dirs)
        .group_by(lambda root: root.split(":/")[0].lower())
        .map(lambda dir: create_file_worker(*dir[1]))
        .list()
    )

    thread = Thread(
        target=all_files_loop,
        args=[workers, output_sender]
    )
    thread.start()

    return (thread, output_recv)

def all_files_loop(workers: List[Tuple[Process, Connection]], output_connection: Connection):

    while seq(workers).map(lambda worker: worker[0].is_alive()).any():
        (seq(workers)
            .map(lambda worker: worker[1])
            .filter(lambda pipe: pipe.poll())
            .for_each(lambda pipe: output_connection.send(pipe.recv()))
        )

        workers = seq(workers).filter(lambda worker: worker[0].is_alive())

def create_file_worker(*root_dirs: str) -> Tuple[Process, Connection]:
    output_recv, output_sender = Pipe(duplex=False)
    
    process = Process(
        target = _get_all_files_in_dir,
        args=[output_sender, *root_dirs]
    )
    process.start()

    return (process, output_recv)


def _get_all_files_in_dir(output_sender: Connection, *root_dirs: str) -> List[str]:
    for root_dir in root_dirs:
        for path, _subdirs, files in os.walk(root_dir):
            for name in files:
                file_name = os.path.join(path, name)

                if file_name.split('.')[-1] in IMG_EXT:
                    output_sender.send(Img(file_name))
                if file_name.split('.')[-1] in VIDEO_EXT:
                    output_sender.send(Video(file_name))
