from typing import List
# from multiprocessing import 
import sys
import os

from functional import seq

from src.file_explorer import all_files

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

    while _p.is_alive():
        print(file_stream.recv())