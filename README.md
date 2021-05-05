# diskette1.py

A tool to extract individual datasets from "IBM Diskette 1" image files.


# About

"Diskette 1" is an ancient format introduced by IBM in the 70s, and usually found in 8 inch floppy disks. Its internals are documented in the pdf file present in this repository (courtesy of bitsavers.org)

If you have an "IBM Diskette 1" image file dumped with a modern universal floppy drive controller board (e.g. Kryoflux, Fluxengine), you can use this tool to extract individual datasets from it.


# Usage

```$ ./diskette1.py --help

usage: diskette1.py [-h] [-i] inputfile

Extract individual data sets from IBM 'Diskette 1' floppy images.

positional arguments:
  inputfile

optional arguments:
  -h, --help       show this help message and exit
  -i, --info-only  Print only metadata from first track. Do not extract
                   individual files.```

