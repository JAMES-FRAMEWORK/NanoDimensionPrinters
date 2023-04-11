# File Resolution Upgrader
This Python script upgrades the resolution parameter value of a Dragonfly printer's machine calibration file based on the resolution of a Dragonfly project file.
## Requirements
This script requires the following packages:

- pandas
- PyQt6

## Usage
- Run the script main.py from the command line on the printer PC.
- Browse for 'yourPrintJobFile.pcbjc', and select it.
- you will see in the text window your resolution and machine resolution. 
- press "change res" for machine resolution adoption to PJ file.
- now you can print this file everything needed changed, and you have stored your previous ST data in: C:\DragonFly\Conf\ST_changes.cfg.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
