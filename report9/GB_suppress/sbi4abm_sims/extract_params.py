import pickle
import sys

def main(pickle_file):
    with open(pickle_file, 'rb') as f:
        params_list = pickle.load(f)

    for params in params_list:
        print(' '.join(map(str, params)))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_params.py <path_to_pickle_file>")
        sys.exit(1)

    pickle_file = sys.argv[1]
    main(pickle_file)
