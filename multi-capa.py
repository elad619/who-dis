import argparse
from genericpath import exists
from tqdm import tqdm
from multiprocessing import Process, Queue, Lock
from subprocess import Popen, DEVNULL, CalledProcessError, PIPE
from os import listdir, mkdir, walk
from os.path import isdir, abspath, basename, dirname
from os.path import join as osjoin

RULES_DIR = "./rules"
SAMPLES_DIR = "./samples"
OUTPUT_DIR = "./out"

CAPA_EXE_PATH = "./capa"

PBAR_LOCK = Lock()

class CapaWorker(Process):
    def __init__(self, queue, pbar, samples, rules, out):
        super(CapaWorker, self).__init__()
        self.queue = queue
        self.progress_bar = pbar
        self.samples = samples
        self.rules = rules
        self.out = out

    def run(self):
        # do init
        # do stuff
        for sample in iter(self.queue.get, None):
            self.execute_capa(sample)
            self.update_progress_bar()
        
    def execute_capa(self, sample):
        # create file names
        mal_family = basename(dirname(sample))
        out_dir = osjoin(self.out, mal_family)
        out_filename = f"{osjoin(out_dir, basename(sample))}-capa.txt"

        # check if file exists
        if exists(out_filename):
            return

        # build command
        capa_command = [CAPA_EXE_PATH, "-r", self.rules, sample]

        # check if parent dir exists
        try:
            if not isdir(out_dir):
                mkdir(out_dir)
        except:
            pass

        out = ""
        capa_process = Popen(capa_command, stdout=PIPE, stderr=PIPE)
        capa_output, capa_error = capa_process.communicate()
        
        out = capa_error if b"ERROR:capa:" in capa_error else capa_output

        with open(out_filename, 'wb') as out_file:
            out_file.write(out)

            
    def update_progress_bar(self):
       PBAR_LOCK.acquire()
       self.progress_bar.update()
       PBAR_LOCK.release() 

def get_samples(path):
    """
    Gets all of the sample from a path
    path: path to folder with samples
    return: all of the samples in the folder
    """
    files = []
    if not isdir(path):
        return []

    for item in listdir(path):
        item = osjoin(path, item)
        if isdir(item):
            files += [osjoin(dp, f) for dp, dn, filenames in walk(item) for f in filenames]
        else:
            files.append(item)
    return files


def main(**kwargs):
    # get params
    samples_dir = kwargs["samples"]
    rules_dir = kwargs["rules"]
    out_dir = kwargs["out"]
    workers = kwargs["workers"]

    samples_queue = Queue()
    samples = get_samples(samples_dir)

    # add progress bar
    progress_bar = tqdm(total = len(samples))

    # add workers
    for i in range(workers):
        CapaWorker(samples_queue, progress_bar, samples_dir, rules_dir, out_dir).start()

    # add samples
    for sample in samples:
        samples_queue.put(sample)

    # kill workers
    for i in range(workers):
        samples_queue.put(None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CAPAs simultaneously')
    parser.add_argument('-s', "--samples", metavar="SAMPLES_DIR", type=str,
                    help='The folder that contains the source samples', nargs='?', default=SAMPLES_DIR)

    parser.add_argument('-r', "--rules", metavar="RULES_DIR", type=str,
                    help='The folder that contains the CAPA rules', nargs='?', default=RULES_DIR)

    parser.add_argument('-o', "--out", metavar="OUT_DIR", type=str,
                    help='The output folder', nargs='?', default=OUTPUT_DIR)

    parser.add_argument('-w', "--workers", metavar="WORKERS", type=int,
                    help='The number of workers', nargs='?', default=1)
    
    main(**vars(parser.parse_args()))
