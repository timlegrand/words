import argparse
import subprocess
import itertools
import time
import math
import threading


def double_check(decoded_file):
    try:
        with open(decoded_file, 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError:
        # text is expected but got binary
        return False
    return True


def try_it(args, passphrase, worker):
    output_filename = args.output_file + str(worker)
    cmd = ["openssl", "enc", "-aes-256-cbc", "-d", "-a", "-in", args.input_file, "-out", output_filename, "-pass", f"pass:{passphrase}"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if not p.returncode:
        return double_check(output_filename)
    return False


def work(worker, words, total_arrangements, until, skip, length, chunk_size):
        num_arrangements = until - skip if until else total_arrangements - skip
        print(f"[#{worker}] Selected range: {skip}-{until if until else total_arrangements} ({num_arrangements}/{total_arrangements})")
        i = 0
        done = 0
        last = time.time()
        for a in itertools.permutations(words, length):
            i += 1
            if skip and i < skip + 1:
                continue
            passphrase = " ".join(a)
            if try_it(args, passphrase, worker):
                print(f"[#{worker}] Possible passphrase: {passphrase}")
            done += 1
            if i % chunk_size == 0:
                now = time.time()
                print(f"[#{worker}] Current try: {i} - Progress: {done / num_arrangements:%} - Speed: {chunk_size / (now - last):.0f} attempts/s")
                last = now
            if until and i >= until:
                break
        print(f"[#{worker}] Finished at {i} - {done / num_arrangements:%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--skip", type=int, default=0, help="number of combinations to skip")
    parser.add_argument("-u", "--until", type=int, default=0, help="combination number where to stop at")
    parser.add_argument("-i", "--input-file", default="test.aes", help="input file, encoded")
    parser.add_argument("-o", "--output-file", default="test.txt", help="output file, decoded")
    parser.add_argument("-w", "--words-file", default="words-test.txt", help="path to file containing the words to build passphrase upon")
    parser.add_argument("-l", "--length", type=int, default=12, help="passphrase length")
    parser.add_argument("-c", "--chunk-size", type=int, default=1000, help="print info every N combinations")
    parser.add_argument("-t", "--threads", type=int, default=1, help="split work among multiple threads")
    args = parser.parse_args()

    with open(args.words_file) as f:
        words = f.read().split()
        total_arrangements = int(math.factorial(len(words)) / math.factorial(len(words) - args.length))  # e.g. 8892185702400 for 12 among 18

    threads = []
    end = args.until if args.until else total_arrangements
    for i in range(args.threads):
        start = int((end - args.skip) / args.threads * i + args.skip)
        until = int((end - args.skip) / args.threads * (i + 1) + args.skip)
        threads.append(threading.Thread(target=work, args=(i, words, total_arrangements, until, start, args.length, args.chunk_size,)))
        threads[i].start()
    for i in range(args.threads):
        threads[i].join()
