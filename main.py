import argparse

from faceRecog import FaceSearch


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Face recognition')
    
    parser.add_argument('--query', type=str, help='query image')
    parser.add_argument('--source', type=str, help='where to search')
    
    args = parser.parse_args()

    query   = args.query
    source  = args.source
    faceSearch = FaceSearch(query, source)
    faceSearch.run()