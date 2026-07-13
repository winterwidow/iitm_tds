import hashlib
import multiprocessing as mp

TOKEN = "96d65dedd0e4801d"
DIFFICULTY = 26


def worker(start, step, token, difficulty, found, result):

    nonce = start

    while not found.is_set():

        data = f"{token}:{nonce}".encode()

        digest = hashlib.sha256(data).digest()

        if int.from_bytes(digest, "big") >> (256 - difficulty) == 0:
            result.value = nonce
            found.set()
            return

        nonce += step


if __name__ == "__main__":

    cpus = mp.cpu_count()

    found = mp.Event()

    result = mp.Value("Q", 0)

    procs = []

    for i in range(cpus):

        p = mp.Process(
            target=worker,
            args=(i, cpus, TOKEN, DIFFICULTY, found, result),
        )

        p.start()

        procs.append(p)

    for p in procs:
        p.join()

    print(result.value)
