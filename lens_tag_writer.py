#!/usr/bin/python3
#
#     F5Exiftag,  A script to read film roll data from files exported
#     by Nikon Photo Secretary for F5 and inject the information into
#     EXIF tags in the jpeg or tiff scans of the film.
#     Copyright © 2026 James McKenzie jrmknz@yahoo.co.uk
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import configparser
import FreeSimpleGUI as sg
from pathlib import Path
from exiftool import ExifToolAlpha, ExifToolHelper
import pandas as pd

from main import script_path, version_number, version_date, my_camera_model, my_camera_serial_number, licence_popup, settings_window, make_filmdata_window

my_nikon_lenses_path = Path('lens_tagging/my_nikon_lenses.csv')

sg.theme('SystemDefault')

config = configparser.ConfigParser()
path_to_config = script_path / 'config.ini'
config.read(path_to_config)

my_nikon_lenses = pd.read_csv(my_nikon_lenses_path)

def get_lens_tags_from_LensIDName(lidname):
    my_lens = my_nikon_lenses.query('LensID == @lidname')
    my_lens_tags = my_lens.values.tolist()
    my_lens_cols = my_lens.columns.tolist()
    return my_lens_cols, my_lens_tags[0]

def save_tags_dict_with_lenses(sd_data_file):
    sd_data_db = pd.read_csv(sd_data_file, header=0)
    progress_layout = [
        [sg.Text('Processing scanned images')],
        [sg.ProgressBar(1, orientation='h', key='progress', size=(25, 15))]
    ]
    progress_win = sg.Window('Processing...', progress_layout, disable_close=True).Finalize()
    progress_win.bring_to_front()
    progress_win.force_focus()
    progress_bar = progress_win.find_element('progress')
    for _, row in sd_data_db.iterrows():
        progress_bar.UpdateBar(row['Frame Count'], len(sd_data_db))
        ShutterSpeed = str(row['Shutter Speed'])
        if ShutterSpeed[-1:] == "'":
            ShutterSpeed = 60 * float(row['Shutter Speed'][:-1])
        elif ShutterSpeed[-1:] != '"':
            ShutterSpeed = "1/" + ShutterSpeed
        else:
            ShutterSpeed = row['Shutter Speed']
        Focal_Length = str(row['Focal Length'])
        tags_dict = {'Model': my_camera_model,
                     'ISO': row['ISO'],
                     'FocalLength': Focal_Length,
                     'FocalLengthIn35mmFormat': Focal_Length,
                     'FNumber': row['Aperture'][1:],
                     'ExposureTime': ShutterSpeed,
                     'SerialNumber': my_camera_serial_number
                     }
        if 'Metering System' in row:
            if row['Metering System'][-6:] == 'Matrix':
                MeteringMode = 'Multi-segment'
            elif row['Metering System'] == 'Center-weighted':
                MeteringMode = 'Center-weighted average'
            else:
                MeteringMode = 'Spot'
            tags_dict.update({'MeteringMode': MeteringMode})
        if 'Day' in row:
            mydate = row['Day'].split('/')
            DateTimeOriginal = mydate[2] + ':' + mydate[0].zfill(2) + ':' + mydate[1].zfill(2) + ' ' + row['Time']
            tags_dict.update({'DateTimeOriginal': DateTimeOriginal,
                              'CreateDate': DateTimeOriginal,
                              'DateCreated': DateTimeOriginal})
        if 'Exposure Mode' in row:
            if row['Exposure Mode'] == 'Aperture-Priority Auto':
                ExposureProgram = 'Aperture-priority AE'
            elif row['Exposure Mode'] == 'Manual Exposure':
                ExposureProgram = 'Manual'
            elif row['Exposure Mode'] == 'Program Exposure':
                ExposureProgram = 'Program AE'
            else:
                ExposureProgram = 'Shutter speed priority AE'
            tags_dict.update({'ExposureProgram': ExposureProgram})
        if 'Exposure Comp.' in row:
            tags_dict.update({'ExposureCompensation': row['Exposure Comp.']})
        ScanImageStem = str(sd_data_file.stem) + "-" + str(row['Frame Count'])
        ScanImageRoot = Path(config.get('ScannedImagesPath', 'path'))
        ScanImagePath = Path(ScanImageRoot / ScanImageStem).with_suffix('.JPG')
        if Path(ScanImageRoot / ScanImageStem).with_suffix('.jpg').is_file():
            ScanImagePath = Path(ScanImageRoot / ScanImageStem).with_suffix('.jpg')
        if ScanImagePath.is_file():
            if isinstance(row['LensIDName'], str):
                lens_cols, lens_tags = get_lens_tags_from_LensIDName(row['LensIDName'])
                with ExifToolAlpha() as eta:
                    eta.copy_tags(lens_tags[0], str(ScanImagePath))
                with ExifToolHelper() as eth:
                    eth.set_tags(ScanImagePath, tags=tags_dict, params=["-P", "-overwrite_original"])
        else:
            sg.popup_error('Scan image could not be found in ' + str(ScanImagePath),
                           'Are the scanned images saved in the right place and with the correct naming ' +
                           'convention? This application will keep going and try the next one in the ' +
                           'sequence until the end of the roll.', title='Error: scanned image not found.')
    progress_win.close()
    return True

def about_popup():
    sg.popup("""This is a tool for Nikon F5 camera users who connect their
camera to a PC or Mac with a serial cable and use Nikon
Photo Secretary for F5 to save the Shooting Data from a
roll of film.

You need to use the "Convert Data" function in Photo
Secretary for F5 to save the shooting data in a text
format readable by this software.

You also need your film scans all saved as JPG and
named according to a strict naming convention. e.g. if
your Shooting Data is saved in a file named
"2550103.txt" then the JPG files must be named
"2550103-1.JPG", "2550103-2.JPG" etc.""",
    "Version " + version_number + " / " + version_date + "\n" +
    "Copyright © " + version_date[-4:] + " JR McKenzie (jrmknz@yahoo.co.uk)\n" +
    "https://github.com/jrmckenzie/F5Exiftag\n",
    title="About F5Exiftag")
    return True

# Read configuration and find location of Nikon Shooting Data folder, or ask user to set it
if config.has_option('NikonSData', 'path'):
    shooting_data_path = config.get('NikonSData', 'path')
else:
    settings_window()

if __name__ == "__main__":
    my_file_type = 'Shooting data with lens info', '*.wld'
    my_desc = ('Tag a batch of scanned files (in jpeg format) with lens data, using the Shooting Data exported' +
                    '  from Nikon Photo Secretary AC-1WE for F5 updated by the user with lens info.')
    my_title = 'F5Exiftag - lens tag writer'
    filmdata_window = make_filmdata_window(my_title, my_desc, my_file_type, True)
    while True:
        fevent, fvalues = filmdata_window.read()
        if fevent == 'Exit' or fevent == sg.WIN_CLOSED:
            sys.exit()
        elif fevent == 'About':
            about_popup()
            continue
        elif fevent == 'Licence':
            licence_popup()
            continue
        elif fevent == 'Go!':
            if fvalues['FDloc'] is None or len(fvalues['FDloc']) <= 1:
                sg.popup('Please browse for the path to your Nikon Shooting Data file and try again.')
                continue
            if fvalues['SIloc'] is None or len(fvalues['SIloc']) <= 1:
                sg.popup('Please browse for the path to your Scanned Images folder and try again.')
                continue
            if not config.has_section('NikonFDataLenses'):
                config.add_section('NikonFDataLenses')
            config.set('NikonFDataLenses', 'path', fvalues['FDloc'])
            config.set('ScannedImagesPath', 'path', fvalues['SIloc'])
            with open(path_to_config, 'w') as iconfigfile:
                config.write(iconfigfile)
                iconfigfile.close()
            sd_data_file = Path(config.get("NikonFDataLenses", "path"))
            tags_dict = save_tags_dict_with_lenses(sd_data_file)
        sg.popup_ok('Process complete for Shooting Data ' +
                    Path(config.get("NikonFDataLenses", "path")).stem + '.', title='Process complete')
