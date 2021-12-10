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
    parser.add_argument("-c", "--chunk-size", type=int, default=1000, help="print info every N combinations")
    args = parser.parse_args()

    with open(args.words_file) as f:
        words = f.read().split()
        total_arrangements = int(math.factorial(len(words)) / math.factorial(len(words) - args.length))  # e.g. 8892185702400 for 12 among 18
        num_arrangements = args.until - args.skip if args.until else total_arrangements - args.skip
        print(f"Selected range: {args.skip}-{args.until if args.until else total_arrangements} ({num_arrangements}/{total_arrangements})")
        i = 0
        done = 0
        last = time.time()
        for a in itertools.permutations(words, args.length):
            i += 1
            if args.skip and i < args.skip + 1:
                continue
            passphrase = " ".join(a)
            if try_it(args, passphrase):
                print(f"Passphrase may be: {passphrase}")
            done += 1
            if i % args.chunk_size == 0:
                now = time.time()
                print(f"Current try: {i} - Progress: {done / num_arrangements:%} - Speed: {args.chunk_size / (now - last):.0f} attempts/s")
                last = now
            if args.until and i >= args.until:
                break
        print(f"Current try: {i} - Progress: {done / num_arrangements:%}")
