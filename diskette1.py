#!/usr/bin/env python3

import argparse, sys, os
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 

p = argparse.ArgumentParser()
p.description = "Extract individual data sets from IBM 'Diskette 1' floppy images."
p.add_argument('inputfile')
p.add_argument("-i", "--info-only", action="store_true", dest="info", help="Print only metadata from first track. Do not extract individual files.")
opts = p.parse_args()

# Input validation
try: f = open(opts.inputfile, "rb")
except:
    print("ERROR: CANNOT READ INPUT FILE " + opts.inputfile)
    sys.exit(1)

### Track 0 

print("")
print("DISK METADATA")
print("=============")
print("")

## sector 01 and 02 are reserved for IPL and IMPL. 
f.seek(0)
b = f.read(128)
check1 = b[:80].hex() == '40'*80
check2 = b[80:].hex() == '00'*48

f.seek(1*128)
b = f.read(128)
check3 = b[:80].hex() == '40'*80
check4 = b[80:].hex() == '00'*48

if check1 and check2 and check3 and check4: ipl = "not present"
else: ipl = "present"
print("IPL / IMPL: " + ipl)

## sector 03 is reserved for system scratch.
f.seek(2*128)
b = f.read(128)
check1 = b[:80].hex() == '40'*80
check2 = b[80:].hex() == '00'*48

if check1 and check2: scratch = "not present"
else: scratch = "present"
print("System scratch: " + scratch)

## sector 04 is reserved
f.seek(3*128)
b = f.read(128)
check1 = b[:80].hex() == '40'*80
check2 = b[80:].hex() == '00'*48

if check1 and check2: reserv = "not present"
else: reserv = "present"
print("Data in reserved sector: " + reserv)

# disk layout looks completely different when IPL/IMPL and/or reserved sectors (01, 02, 04) are present
if ipl == 'present' or reserv == 'present': print(""); sys.exit(0)

## sector 05 (ERMAP)
f.seek(4*128)
b = f.read(128)

check1 = b.decode('cp500')[:5] == 'ERMAP'
if check1: ermap = "present"
if not check1: ermap = "not present"
print("Label ERMAP: " + ermap)

# defective cylinders
deffc_val = b.decode('cp500')[6:8]
if deffc_val == '  ': deffc = "none"
else: deffc = deffc_val

if deffc == "none": print("Defective cylinders: none")
else:
    
    print("First defective cylinder: " + deffc)

    deffc_val = b.decode('cp500')[10:12]
    if deffc_val == '  ': deffc = "none"
    else: deffc = deffc_val
    
    if deffc == "none": pass
    else:
        
        print("Second defective cylinder: " + deffc)  

        deffc_val = b.decode('cp500')[12]
        if deffc_val == ' ': deffc = "No"
        else: deffc = "Yes"
        print("More defective cylinders: " + deffc)  

# diskette defect indicator
deffd_val = b.decode('cp500')[22]
if deffd_val == ' ': deffd = "blank"
else: deffd = deffd_val
print("Diskette defect indicator: " + deffd)

# error directory indicator
deffd_val = b.decode('cp500')[23]
if deffd_val == ' ': deffd = "blank"
else: deffd = deffd_val
print("Error directory indicator: " + deffd)

if deffd == "blank": pass
else: print("Error directory: " + b.decode('cp500')[24:72])

## sector 07 (volume label)
f.seek(6*128)
b = f.read(128)

print("")
print("Volume label: " + b.decode('cp500')[0:4].rstrip())
print("Volume identifier: " + b.decode('cp500')[4:10].rstrip())

deffd_val = b.decode('cp500')[10]
if deffd_val == ' ': deffd = "blank"
else: deffd = deffd_val
print("Volume accessibility field: " + deffd)

deffd_val = b.decode('cp500')[37:51]
if deffd_val == ' '*14: deffd = "blank"
else: deffd = deffd_val.rstrip()
print("Owner identifier field.: " + deffd)

deffd_val = b.decode('cp500')[73]
if deffd_val == ' ': deffd = "blank"
else: deffd = deffd_val
print("Volume surface indicator: " + deffd)

deffd_val = b.decode('cp500')[71]
if deffd_val == ' ': deffd = "blank"
else: deffd = deffd_val
print("Extent arrangement indicator: " + deffd)

deffd_val = b.decode('cp500')[73]
if deffd_val == ' ': deffd = "blank"
else: deffd = deffd_val
print("Special requirements indicator: " + deffd)

d_len = {' ': '128 bytes', '1': '256 bytes', '2': '512 bytes', '3': '1024 bytes'}
ln=d_len[b.decode('cp500')[75]]
print("Length of the physical record (sector) on cylinders 1 through 76: " + ln)
lpr=int(ln.replace(' bytes', ''))

deffd_val = b.decode('cp500')[76:78]
if deffd_val == ' ' or deffd_val == '01': deffd = "(sequential)"
else: deffd = ''
print("Physical record (sector) sequence code: " + deffd_val + " " + deffd)

deffd_val = b.decode('cp500')[79]
if deffd_val == 'W': deffd = "(IBM standard labels are present)"
else: deffd = ""
print("Label standard version field: " + deffd_val + " " + deffd)

print("")
print("DATA SET LABELS")
print("===============")
print("")
print("LB   ID               LEN  ABOE  PEOE  RBSWEMS CD    RL  OFF      ED    VDEOD   ")
print("--------------------------------------------------------------------------------")
records = []
for l in range(7, 26, 1): 
    f.seek(l*128) 
    b = f.read(128)
    record = b.decode('cp500')[:80]
    print(record)
    if record[:5] == 'HDR1 ': records.append(record)

print("")

### Tracks 1-77

if opts.info: sys.exit(0)
else:

    print("DATA SETS EXTRACTION")
    print("====================")
    print("")
 
    d = os.path.basename(opts.inputfile).split('.')[:-1][0]
    try: os.mkdir(d)
    except:
        print("ERROR: CREATION OF DIRECTORY %s FAILED" % d)
        print("")
        sys.exit(1)
    
    tr0_offset = 26*128
    for r in records:

        ds_name = r[5:22].rstrip()
        
        bfile_name = d + "/" + ds_name
        bfile = open(bfile_name, "wb")
        
        afile_name = d + "/" + ds_name + '.ascii'
        afile = open(afile_name, "w")
        
        bln = int(r[22:27])
        
        boe = r[28:33]
        btr = int(boe[:2]) ; bsc = int(boe[-2:])
        
        eod = r[74:79]
        etr = int(eod[:2]) ; esc = int(eod[-2:])
        
        stot = (etr-btr)*26 + esc - (bsc-1) -1
        pos = f.seek(tr0_offset + (btr-1)*26*lpr + (bsc-1)*lpr )

        # ~ print("")
        # ~ print(r[5:22].rstrip(), etr, btr, bsc, esc, stot)
        # ~ print("")
        
        print("-- Saving data set " + ds_name + " (" + str(stot) + " sectors) in binary file: " + bfile_name)
        print("-- Saving ASCII conversion of " + ds_name + " in text file: " + afile_name)
    
        for b in range(0, stot, 1):
            b = f.read(lpr)
            bfile.write(b)
            afile.write(b.decode('cp500')[:bln] + '\n')
            # ~ print(b.decode('cp500')[:bln])
        
        bfile.close()
        afile.close()
        print("")
        
    sys.exit(0)
