# Print Job Log Collector
This script collects and processes print job logs from a printslog folder and time estimation logs folder, saves the output to an excel file, then you can check your usage and statistics. this file ease to modify to get more fields into the excel file.

# Dependencies
This script requires the following dependencies:

- Python 3
- pandas
- PyQt6
- shutil
- zipfile
# Installation
- Install Python 3.
- Install pandas by running `pip install pandas` in the command line.
- Install PyQt6 by running `pip install PyQt6` in the command line.
# Usage
- Deploy the files in DF-IV PC.
- Run the script by running python `main.py` in the command line.
- Click the "Collect Logs" button to collect and process print job logs from the specified folder.
- The output will be saved to `C:/output/statistics.csv`.
- Click the "Exit" button to close the application.
# License
This project is licensed under the MIT License - see the LICENSE file for details.
