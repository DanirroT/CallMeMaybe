import sys
from src import main

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("\rThe program has been forcefully stopped")
