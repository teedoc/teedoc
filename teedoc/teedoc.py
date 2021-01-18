import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="teedoc, a doc generator, generate html from markdown and jupyter notebook")
    parser.add_argument("command", choices=["build", "serve"])
    args = parser.parse_args()
    print(args)
