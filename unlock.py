import argparse
import subprocess
import itertools
import time
import math


def try_it(args, passphrase):
    cmd = [
        "openssl", "enc", "-aes-256-cbc",
        "-d",  # decrypt
        "-a",  # Base64 encode/decode
        # "-p",  # Print the iv/key when encoding
        "-in", args.input_file,
        "-out", args.output_file,
        "-pass", f"pass:{passphrase}"
        ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return not p.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--skip", type=int, default=0, help="number of combinations to skip")
    parser.add_argument("-u", "--until", type=int, default=0, help="combination number where to stop at")
    parser.add_argument("-i", "--input-file", default="test.aes", help="input file, encoded")
    parser.add_argument("-o", "--output-file", default="test.txt", help="output file, decoded")
    parser.add_argument("-w", "--words-file", default="words-test.txt", help="path to file containing the words to build passphrase upon")
    parser.add_argument("-l", "--length", type=int, default=12, help="passphrase length")
    args = parser.parse_args()

    with open(args.words_file) as f:
        words = f.read().split()
        num_arrangements = math.factorial(len(words)) / math.factorial(len(words) - args.length)  # e.g. 8892185702400 for 12 among 18
        i = 0
        last = time.time()
        for a in itertools.permutations(words, args.length):
            i += 1
            if args.skip and i < args.skip + 1:
                continue
            passphrase = " ".join(a)
            if try_it(args, passphrase):
                print(passphrase)
                break
            if i % 1000 == 0:
                now = time.time()
                print(f"Current try: {i} - Progress: {i / num_arrangements:%} - Speed: {1000 / (now - last):.0f} tries/s")
                last = now
            if args.until and i >= args.until:
                break
