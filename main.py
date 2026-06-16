#!/usr/bin/python3
#
#     F5Exiftag,  A script to read film roll data from files exported
#     by Nikon Photo Secretary and inject the information into EXIF
#     tags in the jpeg or tiff scans of the film.
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
from exiftool import ExifToolHelper
import pandas as pd
from datetime import datetime, timedelta

version_number = '1.0.1-beta-1'
version_date = '16/06/2026'
ISO = 100

sg.theme('DarkBrown2')
sg.theme_background_color('#333333')
sg.theme_text_element_background_color('#333333')
sg.theme_button_color('#FFE100')

config = configparser.ConfigParser()
script_path = Path(__file__).absolute().parent
path_to_config = script_path / 'config.ini'
config.read(path_to_config)

def licence_popup():
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
    return True

def about_popup():
    sg.popup("""This is a tool for Nikon F5/F90/F90x/F100 SLR users
who connect their camera to a PC or Mac with a serial
cable and use Nikon Photo Secretary to download the
Shooting Data for a roll of film from the camera's
memory to their computer.

Its purpose is to tag JPG film scans with metadata
based on the Shooting Data (shutter speed, aperture, 
focal length etc.)

You need to use the "Convert Data" or "Save As" function
in Photo Secretary to save the shooting data in a text
format readable by this utility.

You also need your film scans all saved as JPG and
named according to a strict naming convention. e.g. if
your Shooting Data is saved in a file named
"2550103.txt" then the JPG files must be named
"2550103-1.JPG", "2550103-2.JPG" etc.\n""",
    "Version " + version_number + " / " + version_date + "\n\n" +
    "Copyright © " + version_date[-4:] + " JR McKenzie (jrmknz@yahoo.co.uk)\n" +
    "https://github.com/jrmckenzie/F5Exiftag\n",
    title="About F5Exiftag")
    return True

def sd_data_read(my_sd_filename):
    if my_sd_filename.suffix == '.wld':
        return pd.read_csv(my_sd_filename, header=0)
    sd_data_db_firstrow = pd.read_csv(my_sd_filename, header=None, nrows=1)
    if sd_data_db_firstrow.iloc[0, 0] == 'Film Title':
        # This file was created by AC-1WE Photo Secretary for F5
        # comma delimited, first row contains film iso, title and comments, headers in second row
        ISO = int(str(sd_data_db_firstrow.iloc[0, 3]).strip())
        sd_data_db = pd.read_csv(my_sd_filename, header=1)
    else:
        # Assume this file was created by AC-2WE Photo Secretary II for F100
        # tab delimited, first row contains film iso, title and comments, no headers
        sd_data_db_firstrow = pd.read_csv(my_sd_filename, sep='\t', header=None, nrows=1)
        ISO = int(str(sd_data_db_firstrow.iloc[0, 0]).strip())
        sd_data_cols = ['Frame Count', 'Shutter Speed', 'Aperture', 'Focal Length', 'Max. Aperture', 'Metering System',
                        'Exposure Mode', 'Flash Sync Mode', 'Exposure Comp.', 'J', 'K', 'L', 'Data Imprinting', 'Day',
                        'Time']
        sd_data_db = pd.read_csv(my_sd_filename, header=None, skiprows=1, sep='\t',
                                 usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], names=sd_data_cols)
    return ISO, sd_data_db


def settings_window():
    sd_dir = ''
    camera_model = 'Nikon F5'
    camera_serial_nr = ''
    my_timedelta = 0
    if config.has_option('NikonSData', 'path'):
        sd_dir = config.get('NikonSData', 'path')
    if config.has_option('CameraModel', 'name'):
        camera_model = config.get('CameraModel', 'name')
    if config.has_option('CameraSerialNr', camera_model[6:].lower()):
        camera_serial_nr = config.get('CameraSerialNr', camera_model[6:].lower() or '')
    if config.has_option('TimeDelta', 'seconds'):
        my_timedelta = int(config.get('TimeDelta', 'seconds') or '0')
    loclayout = [[sg.Text('F5Exiftag', text_color='#FFE100', font=('Arial', 14, 'bold', 'italic'))],
                 [sg.Text('Please locate your Nikon Photo Secretary Shooting Data folder:')],
                  [sg.Input(key='-IN2-', default_text=sd_dir, change_submits=False,
                           readonly=True),
                  sg.FolderBrowse(key='SDloc', initial_folder=sd_dir)],
                 [sg.Text('Camera model:'), sg.Combo(['Nikon F5', 'Nikon F90', 'Nikon F90x', 'Nikon F100',
                                                     'Nikon F6'], default_value=camera_model, readonly=True,
                                                     key='-MODEL-', enable_events=True),
                  sg.Text('Camera serial number:'), sg.Input(key='-SERIAL-', size=8, default_text=camera_serial_nr)],
                 [sg.Text('Time shift (seconds):'), sg.Input(key='-TSHIFT-', size=11, default_text=my_timedelta)],
                 [sg.Button('Save'), sg.Button('Cancel')]]
    locwindow = sg.Window('Settings', loclayout, finalize=True)
    while True:
        event, values = locwindow.read()
        if event == sg.WIN_CLOSED:
                sg.popup('You must specify the path to your Nikon Shooting Data folder for this application to work. '
                         'The application will now close.')
                sys.exit()
        elif event == 'Save':
            if values['SDloc'] is not None and len(values['SDloc']) > 1:
                shooting_data_path = values['SDloc']
            elif config.has_option('NikonSData', 'path'):
                shooting_data_path = config.get('NikonSData', 'path')
            else:
                sg.popup('Please browse for the path to your Nikon Shooting Data folder and try again.')
                continue
            if not config.has_section('NikonSData'):
                config.add_section('NikonSData')
            config.set('NikonSData', 'path', shooting_data_path)
            if not config.has_section('CameraModel'):
                config.add_section('CameraModel')
            config.set('CameraModel', 'name', values['-MODEL-'])
            if not config.has_section('CameraSerialNr'):
                config.add_section('CameraSerialNr')
            config.set('CameraSerialNr', values['-MODEL-'][6:], values['-SERIAL-'])
            if not config.has_section('ScannedImagesPath'):
                config.add_section('ScannedImagesPath')
            config.set('ScannedImagesPath', 'path', shooting_data_path)
            if not config.has_section('TimeDelta'):
                config.add_section('TimeDelta')
            config.set('TimeDelta', 'seconds', values['-TSHIFT-'])
            with open(path_to_config, 'w') as iconfigfile:
                config.write(iconfigfile)
                iconfigfile.close()
            break
        elif event == 'Cancel':
            if not config.has_option('NikonSData', 'path'):
                sg.popup('Please browse for the path to your Nikon Shooting Data folder and try again.')
                continue
            break
        elif event == '-MODEL-':
            if config.has_option('CameraSerialNr', values['-MODEL-'][6:].lower()):
                camera_serial_nr = config.get('CameraSerialNr', values['-MODEL-'][6:].lower())
            else:
                camera_serial_nr = ''
            locwindow['-SERIAL-'].update(camera_serial_nr)
            continue
    locwindow.close()
    return True


def make_filmdata_window(program_title, program_desc, my_file_type, scans_y):
    fd_layout = [[sg.Text('F5Exiftag', text_color='#FFE100', font=('Arial', 14, 'bold', 'italic'))],
                 [sg.Text('Tag Nikon F5/F90/F90x/F100 film scans with'
                          '\nNikon Photo Secretary shooting data', font=('Arial', 12))],
                 [sg.Text('Please locate your Nikon Photo Secretary Shooting Data file:', pad=(5,(12,0)))],
                 [sg.Input(key='-MODEL-', change_submits=False, readonly=True),
                  sg.FileBrowse(key='FDloc', initial_folder=config.get('NikonSData', 'path'),
                                file_types=((my_file_type), ('All Files', '*.*')))]]
    if scans_y:
        fd_layout = [fd_layout, [sg.Text('Please locate your Scanned Images folder:', pad=(5,(14,0)))],
                 [sg.Input(key='-SERIAL-', change_submits=False, readonly=True),
                  sg.FolderBrowse(key='SIloc', initial_folder=config.get('ScannedImagesPath', 'path')), ]]
        if config.has_option('TimeDelta', 'seconds'):
            my_timedelta = int(config.get('TimeDelta', 'seconds') or '0')
            if my_timedelta > 0:
                fd_layout = [fd_layout, [sg.Text('Attention: you have a timeshift of ' + str(my_timedelta) +
                                                 ' seconds configured.\nClick Settings if you want to change it.',
                                                 pad=(5,(14,0)), text_color='#FFE100')]]
    fd_layout = [fd_layout, [sg.Button('Go!', pad=(5,14)), sg.Button('About'), sg.Button('Settings'),
                             sg.Button('Licence'), sg.Button('Exit')],
                            [sg.Text('v' + version_number + ' Copyright © ' + version_date[-4:] + ' JR McKenzie',
                                     font=('Arial', 8, 'normal'))]]
    return sg.Window(program_title, fd_layout, finalize=True)

def save_tags_dict(sd_data_file):
    global ISO
    # Iterate through the frames on the film - but first, pop up a progress bar window
    progress_layout = [
        [sg.Text('Processing scanned images')],
        [sg.ProgressBar(1, orientation='h', key='progress', size=(25, 15))]
    ]
    progress_win = sg.Window('Processing...', progress_layout, disable_close=True).Finalize()
    progress_win.bring_to_front()
    progress_win.force_focus()
    progress_bar = progress_win.find_element('progress')
    my_camera_model = 'Nikon F5'
    my_camera_serial_number = ''
    my_timedelta = 0
    if config.has_option('CameraModel', 'name'):
        my_camera_model = config.get('CameraModel', 'name')
    if config.has_option('CameraSerialNr', my_camera_model[6:].lower()):
        my_camera_serial_number = config.get('CameraSerialNr', my_camera_model[6:].lower() or '')
    if config.has_option('TimeDelta', 'seconds'):
        my_timedelta = int(config.get('TimeDelta', 'seconds') or '0')
    ISO, sd_data_db = sd_data_read(sd_data_file)
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
        tags_dict = {'Lens': Focal_Length + 'mm f/' + str(row['Max. Aperture'])[1:],
                     'ISO': ISO,
                     'FocalLength': Focal_Length,
                     'FocalLengthIn35mmFormat': Focal_Length,
                     'FNumber': row['Aperture'][1:],
                     'ExposureTime': ShutterSpeed,
                     }
        if len(my_camera_serial_number) > 0:
            tags_dict.update({'SerialNumber': int(my_camera_serial_number)})
        if len(my_camera_model) > 0:
            tags_dict.update({'Model': my_camera_model})
        if 'Metering System' in row:
            if row['Metering System'][-6:] == 'Matrix':
                MeteringMode = 'Multi-segment'
            elif row['Metering System'] == 'Center-weighted':
                MeteringMode = 'Center-weighted average'
            else:
                MeteringMode = 'Spot'
            tags_dict.update({'MeteringMode': MeteringMode})
        if 'Day' in row:
            if not pd.isna(row['Day']):
                sd_date_format = '%m/%d/%Y %H:%M:%S'
                my_date = datetime.strptime(row['Day'] + ' ' + row['Time'], sd_date_format)
                my_date = my_date + timedelta(seconds=my_timedelta)
                exiftool_date_format = '%Y:%m:%d %H:%M:%S'
                DateTimeOriginal = my_date.strftime(exiftool_date_format)
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
                           'sequence until the end of the roll.', title='Warning: scanned image not found.')
    progress_win.close()
    return True

if __name__ == "__main__":
    if config.has_option('NikonSData', 'path'):
        shooting_data_path = config.get('NikonSData', 'path')
    else:
        settings_window()
    my_file_type = 'Shooting data text files', '*.txt'
    my_desc = ('Tag a batch of scanned files (in jpeg format) with the Shooting Data exported from Nikon' +
                    ' Photo Secretary AC-1WE for F5')
    my_title = 'F5Exiftag'
    filmdata_window = make_filmdata_window(my_title, my_desc, my_file_type, True)
    while True:
        event, values = filmdata_window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            sys.exit()
        elif event == 'About':
            about_popup()
            continue
        elif event == 'Settings':
            filmdata_window.close()
            settings_window()
            filmdata_window = make_filmdata_window(my_title, my_desc, my_file_type, True)
            continue
        elif event == 'Licence':
            licence_popup()
            continue
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
            sd_data_file = Path(values['FDloc'])
            tags_dict = save_tags_dict(sd_data_file)
            sg.popup_ok('Process complete for Shooting Data ' +
                        Path(config.get('NikonFData', 'path')).stem + '.', title='Process complete')
            continue