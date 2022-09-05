from genericpath import exists
import io
import argparse
from os import listdir, walk, mkdir
from os.path import join as osjoin, isdir, basename, dirname
import shutil

CAPA_ERROR = b"ERROR:capa"

def get_length(stream: io.BytesIO):
	# Save original spot
	start = stream.tell()
	
	# Get end
	stream.seek(0, io.SEEK_END)
	end = stream.tell()
	
	# Reset back to original spot
	stream.seek(start, io.SEEK_SET)

	return end - start

def is_capa_error(stream: io.BytesIO):
	# Return true if the data contains an error
	data = stream.read(len(CAPA_ERROR))
	return data == CAPA_ERROR

def get_all_files(path):
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

def process_file(item, out_dir):
	"""
	Processses a single file and chooses whether to copy it or not
	@item: the item to check and copy
	@out_dir: the base dir
	"""

	mal_family = basename(dirname(item))
	out_dir = osjoin(out_dir, mal_family)

	if not exists(out_dir):
		mkdir(out_dir)

	out_filename = f"{osjoin(out_dir, basename(item))}"
	with open(item, "rb") as in_stream:
		if get_length(in_stream) > 0 and not is_capa_error(in_stream):
			shutil.copyfile(item, out_filename)

def main(**kwargs):
	in_dir = kwargs["directory"]
	out_dir = kwargs["output"]

	# Make sure the directories exist
	if not exists(in_dir):
		mkdir(in_dir)
	if not exists(out_dir):
		mkdir(out_dir)

	# Iterate over all the files
	files = get_all_files(in_dir)
	for item in files:
		process_file(item, out_dir)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Run CAPAs simultaneously')
	parser.add_argument('-d', "--directory", type=str,
					help='The folder that contains the results to filter', nargs='?', default="out")
	parser.add_argument('-o', "--output", type=str,
					help='The folder that contains the results to filter', nargs='?', default="filtered_out")
	main(**vars(parser.parse_args()))