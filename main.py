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

import csv
import sys
import os
import configparser
import FreeSimpleGUI as sg
from pathlib import Path
from exiftool import ExifToolHelper

version_number = '1.0.0'
version_date = '01/03/2026'
sg.theme('SystemDefault')
config = configparser.ConfigParser()
script_path = Path(os.path.abspath(os.path.dirname(sys.argv[0])))
path_to_config = script_path / 'config.ini'
config.read(path_to_config)
# Read configuration and find location of Nikon Shooting Data folder, or ask user to set it
if config.has_option('NikonSData', 'path'):
    shooting_data_path = config.get('NikonSData', 'path')
else:
    loclayout = [[sg.T('')],
                 [sg.Text('Please locate your Nikon Shooting Data folder:'), sg.Input(key='-IN2-', change_submits=False,
                                                                                      readonly=True),
                  sg.FolderBrowse(key='SDloc')], [sg.Button('Save')]]
    locwindow = sg.Window('Configure path to Nikon Shooting Data folder', loclayout)
    while True:
        event, values = locwindow.read()
        if event == sg.WIN_CLOSED:
            if values is not None:
                if values['SDloc'] is not None and len(values['SDloc']) > 1:
                    break
            else:
                sg.popup('You must specify the path to your Nikon Shooting Data folder for this application to work. '
                         'The application will now close.')
                sys.exit()
        elif event == 'Save':
            if values['SDloc'] is not None and len(values['SDloc']) > 1:
                shooting_data_path = values['SDloc']
            else:
                sg.popup('Please browse for the path to your Nikon Shooting Data folder and try again.')
                continue
            if not config.has_section('NikonSData'):
                config.add_section('NikonSData')
            if not config.has_section('ScannedImagesPath'):
                config.add_section('ScannedImagesPath')
            config.set('NikonSData', 'path', values['SDloc'])
            config.set('ScannedImagesPath', 'path', values['SDloc'])
            with open(path_to_config, 'w') as iconfigfile:
                config.write(iconfigfile)
                iconfigfile.close()
            break
    locwindow.close()

fd_layout = [[sg.Text('F5Exiftag - Tag Nikon F5 film scans with EXIF data', font=('Arial', 12, 'bold'))],
             [sg.Text('Tag a batch of scanned files (in jpeg format) with the Shooting Data exported from Nikon' +
                    'Photo Secretary AC-1WE for F5', size=(45, 3))],
             [sg.Text('Please locate your Nikon Shooting Data file:')],
             [sg.Input(key='-IN3-', change_submits=False, readonly=True),
            sg.FileBrowse(key='FDloc', initial_folder=config.get('NikonSData', 'path'), file_types=(("Text documents (*.txt)", "*.txt"),("All Files", "*.*")))],
             [sg.Text('Please locate your Scanned Images folder:')],
             [sg.Input(key='-IN4-', change_submits=False, readonly=True),
            sg.FolderBrowse(key='SIloc', initial_folder=config.get('ScannedImagesPath', 'path')), ],
             [sg.Button('Go!'), sg.Button('About'), sg.Button('Licence'), sg.Button('Exit')],
             [sg.Text('Copyright © ' + version_date[-4:] + ' JR McKenzie',
                    font=('Arial', 8, 'normal'))],
             ]


def import_data_from_csv(csv_filename):
    try:
        with open(csv_filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            csv_rownum = 0
            csv_data_db = []
            for csvRow in reader:
                sdata = {}
                if csv_rownum == 0:
                    film_iso = csvRow[3]
                elif csv_rownum == 1:
                    dnames = csvRow
                else:
                    colnum = 0
                    for col in csvRow:
                        sdata.update({dnames[colnum]: col})
                        colnum += 1
                    sdata.update({'ISO': film_iso})
                    csv_data_db.append(sdata)
                csv_rownum += 1
            return csv_data_db
    except FileNotFoundError:
        sg.popup('Error: Shooting Data file ' + csv_filename + ' not found.')
        sys.exit('Error: Shooting Data file ' + csv_filename + ' not found.')


if __name__ == "__main__":
    filmdata_window = sg.Window('F5Exiftag', fd_layout)
    while True:
        event, values = filmdata_window.read()
        if event == sg.WIN_CLOSED:
            if values is not None:
                if values['FDloc'] is not None and len(values['FDloc']) > 1 and values['SIloc'] is not None and len(
                        values['SIloc']) > 1:
                    break
            else:
                sg.popup(
                    'You must specify the path to your Nikon Shooting Data file and your Scanned Images folder ' +
                    'for this application to work. The application will now close.')
                sys.exit()
        elif event == 'Exit':
            sys.exit()
        elif event == 'About':
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
        elif event == 'Licence':
            sg.popup("""This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.""",
                     title="Licence", line_width=80)
        elif event == 'Go!':
            if values['FDloc'] is None or len(values['FDloc']) <= 1:
                sg.popup('Please browse for the path to your Nikon Shooting Data file and try again.')
                continue
            if values['SIloc'] is None or len(values['SIloc']) <= 1:
                sg.popup('Please browse for the path to your Scanned Images folder and try again.')
                continue
            if not config.has_section('NikonFData'):
                config.add_section('NikonFData')
            config.set('NikonFData', 'path', values['FDloc'])
            config.set('ScannedImagesPath', 'path', values['SIloc'])
            with open(path_to_config, 'w') as iconfigfile:
                config.write(iconfigfile)
                iconfigfile.close()
            sdatadb = import_data_from_csv(config.get("NikonFData", "path"))
            scanned_images_path = config.get("ScannedImagesPath", "path")
            # Iterate through the frames on the film - pop up a progress bar window
            progress_layout = [
                [sg.Text('Processing scanned images')],
                [sg.ProgressBar(1, orientation='h', key='progress', size=(25, 15))]
            ]
            progress_win = sg.Window('Processing...', progress_layout, disable_close=True).Finalize()
            progress_win.bring_to_front()
            progress_win.force_focus()
            progress_bar = progress_win.find_element('progress')
            for row in sdatadb:
                progress_bar.UpdateBar(row['Frame Count'], len(sdatadb))
                if row['Shutter Speed'][-1:] == '"':
                    ShutterSpeed = row['Shutter Speed'][:-1]
                elif row['Shutter Speed'][-1:] == "'":
                    ShutterSpeed = 60 * float(row['Shutter Speed'][:-1])
                else:
                    ShutterSpeed = "1/" + row['Shutter Speed']
                tags_dict = {"Make": "Nikon",
                             "Model": "F5",
                             "Lens": row['Focal Length'] + "mm f/" + row['Max. Aperture'][1:],
                             "ISO": row['ISO'],
                             "FocalLength": row['Focal Length'],
                             "FocalLengthIn35mmFormat": row['Focal Length'],
                             "FNumber": row['Aperture'][1:],
                             "ExposureTime": ShutterSpeed
                             }
                if 'Metering System' in row:
                    if row['Metering System'][-6:] == 'Matrix':
                        MeteringMode = "Multi-segment"
                    elif row['Metering System'] == 'Center-weighted':
                        MeteringMode = "Center-weighted average"
                    else:
                        MeteringMode = "Spot"
                    tags_dict.update({'MeteringMode': MeteringMode})
                if 'Day' in row:
                    mydate = row['Day'].split("/")
                    DateTimeOriginal = mydate[2] + ":" + mydate[0].zfill(2) + ":" + mydate[1].zfill(2) + " " + row[
                        'Time']
                    tags_dict.update({'DateTimeOriginal': DateTimeOriginal})
                if 'Exposure Mode' in row:
                    if row['Exposure Mode'] == "Aperture-Priority Auto":
                        ExposureProgram = "Aperture-priority AE"
                    elif row['Exposure Mode'] == "Manual Exposure":
                        ExposureProgram = "Manual"
                    elif row['Exposure Mode'] == "Program Exposure":
                        ExposureProgram = "Program AE"
                    else:
                        ExposureProgram = "Shutter speed priority AE"
                    tags_dict.update({'ExposureProgram': ExposureProgram})
                if 'Exposure Comp.' in row:
                    tags_dict.update({"ExposureCompensation": row['Exposure Comp.']})
                ScanImageStem = (Path(config.get("NikonFData", "path")).stem +
                                 "-" + row['Frame Count'])
                ScanImageRoot = Path(config.get("ScannedImagesPath", "path"))
                ScanImagePath = Path(ScanImageRoot / ScanImageStem).with_suffix(".JPG")
                if Path(ScanImageRoot / ScanImageStem).with_suffix(".jpg").is_file():
                    ScanImagePath = Path(ScanImageRoot / ScanImageStem).with_suffix(".jpg")
                if ScanImagePath.is_file():
                    with ExifToolHelper() as et:
                        et.set_tags(
                            ScanImagePath,
                            tags=tags_dict,
                            params=["-P", "-overwrite_original"]
                        )
                else:
                    sg.popup_error('Scan image could not be found in ' + str(ScanImagePath),
                                   'Are the scanned images saved in the right place and with the correct naming ' +
                                   'convention? This application will keep going and try the next one in the ' +
                                   'sequence until the end of the roll.', title='Error: scanned image not found.')
            progress_win.close()
            sg.popup_ok("Process complete for Shooting Data " +
                        Path(config.get("NikonFData", "path")).stem, title="Process complete")
