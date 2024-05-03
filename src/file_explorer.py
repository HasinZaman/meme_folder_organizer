from typing import List, Tuple, Set
import os

from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection

from functional import seq

TARGET_EXT: Set[str] = set(["png", "jpg", "jpeg", "mp4", "avi", "mov"])

def all_files(*roots: str) -> List[str]:

    workers = (seq(roots)
        .map(lambda root: create_file_worker(root))
        .list()
    )

    files: List[str] = []

    while seq(workers).map(lambda worker: worker[1].is_alive()).any():
        (seq(workers)
            .map(lambda worker: worker[0])
            .filter(lambda pipe: pipe.poll())
            .for_each(lambda pipe: files.append(pipe.recv()))
        )

        workers = seq(workers).filter(lambda worker: worker[1].is_alive())
    
    return files


def create_file_worker(start_root: str) -> Tuple[Connection, Process]:
    output_recv, output_sender = Pipe(duplex=False)
    
    process = Process(
        target = _get_all_files_in_dir,
        args=[start_root, output_sender]
    )
    process.start()

    return (output_recv, process)


def _get_all_files_in_dir(root_dir: str, output_sender: Connection) -> List[str]:
    for path, _subdirs, files in os.walk(root_dir):
        for name in files:
            file_name = os.path.join(path, name)

            if file_name.split('.')[-1] in TARGET_EXT:
                output_sender.send(file_name)
