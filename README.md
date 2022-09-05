# who-dis

Multi-Capa 
---------------------
Multi capa runs capa on a large set of files by spreading the
work over multiple pre-defined number of workers.
All the samples come in as a dir of files to process, and the result is a dir with all the text outputs.

There are 2 steps to running the scripts:
- Running multi-capa.py - to execute capa and generate the results. <br>
	You can run it simply by running <br>
	<code> python ./multi-capa.py</code> <br>
	Optionally you can specify also the input directory, output directory, rules directory and number of workers by using flags (--help for more info). Its recommended to set the number of workers to the number of CPU's if applicable.
	The input directory is iterated recursively so you can also split the samples by types
- Running filter_results.py - to filter out all the errors that arised from capa and only leave valid data. <br>
	You can run it by executing <br>
	<code> python ./filter_results.py </code> <br>
	Optioanlly you can also use flags to specify the input and output directories. (--help for more info)
