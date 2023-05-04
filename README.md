# Scripts to Automate Nano-Dimension Printers.
This branch contains a collection of scripts designed to automate and simplify the use of the Nano-Dimension printer.

# short description
## DF-IV-Logger
create custom logs from the printjob log files and log files.

## DF-IV-logs-to-excel
using logs/stats folder and collect the printjobs logs text files to sort it in excell file for better analysys.

## DF-IV-real-ink-status-log
using Printer access to the load cells readings and read the value every X seconds (20 by default), these reading the script put into excell file. the script collects CI load cell, DI load cell, filling seconadary CI, filling secondary DI.
it is possible to use any of the data inside the PLC SW.

## DF-IV-resolution-changer
make it possible to change the resolution of the printer ( adopt the ST of the printer to correct resolution) and save the previous value into calibration folder.

## DF-IV-to-LDM
adopt the PCBJC file to meet the requirements of LDM printer.

# License
This project is licensed under the MIT License - see the LICENSE file for details.
