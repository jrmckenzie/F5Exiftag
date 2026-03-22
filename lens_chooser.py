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
from pathlib import Path
import FreeSimpleGUI as sg
import pandas as pd

from main import script_path, version_number, version_date, licence_popup, set_shooting_data_dir, make_filmdata_window

sg.theme('SystemDefault')
config = configparser.ConfigParser()
path_to_config = script_path / 'config.ini'
my_nikon_lenses_path = script_path / "lens_tagging" / "my_nikon_lenses.csv"
ISO = 100

config.read(path_to_config)
film_lens_chooser_active = False

def make_lens_chooser_window(my_sd_filename):
    sd_data_db = pd.read_csv(my_sd_filename, header=1)
    lens_layout = []
    for _, row in sd_data_db.iterrows():
        lens_layout = lens_layout + [
            [sg.T(row['Frame Count']), sg.T(str(row['Focal Length']) + "mm"), sg.T(str(row['Max. Aperture'])),
             sg.Combo(my_lens_id_list, key=row['Frame Count'], readonly=False)]]
    lens_layout = lens_layout + [[sg.Button('Save'), sg.Button('Cancel')]]
    this_layout = [[sg.Column(lens_layout, scrollable=False, vertical_scroll_only=True)]]
    return sg.Window('Lens chooser', this_layout, finalize=True)

config.read(path_to_config)
# Read configuration and find location of Nikon Shooting Data folder, or ask user to set it
if config.has_option('NikonSData', 'path'):
    shooting_data_path = config.get('NikonSData', 'path')
else:
    set_shooting_data_dir()

if __name__ == "__main__":
    my_desc = ('Choose the lenses matching each frame in the Shooting Data previously imported' +
                            ' from Nikon Photo Secretary AC-1WE for F5.')
    my_title = 'F5Exiftool - lens chooser'
    my_file_type = 'Text documents', '*.txt'
    my_nikon_lenses_db = pd.read_csv(my_nikon_lenses_path, index_col=0)
    my_lens_id_list = my_nikon_lenses_db["LensID"].values.tolist()
    filmdata_window = make_filmdata_window(my_title, my_desc, my_file_type, False)
    while True:
        event, values = filmdata_window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
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
            licence_popup()
            continue
        elif event == 'Go!' and not film_lens_chooser_active:
            if values['FDloc'] is None or len(values['FDloc']) <= 1:
                sg.popup('Please browse for the path to your Nikon Shooting Data file and try again.')
                continue
            film_lens_chooser_active = True
            filmdata_window.hide()
            if not config.has_section('NikonFData'):
                config.add_section('NikonFData')
            if not config.has_section('NikonFDataLenses'):
                config.add_section('NikonFDataLenses')
            sd_filename = values['FDloc']
            sd_with_lenses_path = Path(sd_filename).with_suffix('.wld')
            config.set('NikonFData', 'path', values['FDloc'])
            config.set('NikonFDataLenses', 'path', str(sd_with_lenses_path))
            with open(path_to_config, 'w') as iconfigfile:
                config.write(iconfigfile)
                iconfigfile.close()
            film_lens_chooser = make_lens_chooser_window(values['FDloc'])
            sd_data_db_firstrow = pd.read_csv(sd_filename, header=None, nrows=1)
            ISO = sd_data_db_firstrow.iloc[0,3]
            while True:
                fevent, fvalues = film_lens_chooser.Read()
                if fevent == 'Cancel' or fevent == sg.WIN_CLOSED:
                    film_lens_chooser.close()
                    film_lens_chooser_active = False
                    filmdata_window.un_hide()
                    break
                elif fevent == 'Save':
                    sd_data_db = pd.read_csv(sd_filename, header=1)
                    sd_data_db.insert(5, 'ISO', ISO)
                    sd_data_db.insert(5, 'LensIDName', fvalues.values())
                    sd_data_db.to_csv(sd_with_lenses_path, index=False)
                    sg.popup_ok('Process complete for Shooting Data ' +
                                Path(config.get('NikonFData', 'path')).stem +
                                ".", title='Process complete')
                    film_lens_chooser.close()
                    film_lens_chooser_active = False
                    filmdata_window.un_hide()
                    break