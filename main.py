from typing import List
# from multiprocessing import 
import sys
import os

from functional import seq

from src.file_explorer import all_files, Img, Video
from src.image.caption import caption_worker
from src.image.text_extraction import text_extraction_worker

def get_roots() -> List[str]:
    """
    Gets all the search directories from the system arguments

    return (List[str]): List of valid paths to search
    """
    args = sys.argv[1:]

    if len(args) == 0:
        return []
    
    return (seq(args)
        .sliding(2)
        .filter(lambda pair: pair[0] == "-p" and os.path.exists(os.path.dirname(pair[1])))
        .map(lambda path: path[1])
        .list()
    )

if __name__ == "__main__":
    _p, file_stream = all_files(*get_roots())
    
    c_i, c_o, c_p = text_extraction_worker()

    i = 0

    while _p.is_alive():
        match file_stream.recv():
            case Img(path):
                print(f"img: {path}")
                c_i.send(path)
                print(c_o.recv())
                i+=1
                if i > 3:
                    c_p.kill()
                    break
            case Video(path):
                pass