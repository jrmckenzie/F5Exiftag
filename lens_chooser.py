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
from pathlib import Path
import FreeSimpleGUI as sg
import pandas as pd
from main import (script_path, licence_popup, settings_window, sd_data_read,
                  about_popup, make_filmdata_window, config, path_to_config)

sg.theme('DarkBrown2')
sg.theme_background_color('#333333')
sg.theme_text_element_background_color('#333333')
sg.theme_button_color('#FFE100')

config.read(path_to_config)
my_nikon_lenses_path = script_path / "lens_tagging" / "my_nikon_lenses.csv"
film_lens_chooser_active = False

def make_lens_chooser_window(my_sd_filename):
    ISO, sd_data_db = sd_data_read(my_sd_filename)
    lens_layout = []
    for _, row in sd_data_db.iterrows():
        if pd.isna(row['Focal Length']):
            focal_length = '--mm'
        else:
            focal_length = str(row['Focal Length']) + 'mm'
        if pd.isna(row['Max. Aperture']):
            max_aperture = 'F--'
        else:
            max_aperture = row['Max. Aperture']
        lens_layout = lens_layout + [
            [sg.T(row['Frame Count']), sg.T(focal_length), sg.T(max_aperture),
             sg.Combo(my_lens_id_list, key=row['Frame Count'], readonly=False)]]
    lens_layout = lens_layout + [[sg.Button('Save'), sg.Button('Cancel')]]
    this_layout = [[sg.Column(lens_layout, scrollable=True, vertical_scroll_only=True)]]
    return sg.Window('Lens chooser', this_layout, finalize=True)

# Read configuration and find location of Nikon Shooting Data folder, or ask user to set it
if config.has_option('NikonSData', 'path'):
    shooting_data_path = config.get('NikonSData', 'path')
else:
    settings_window()

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
            about_popup()
            continue
        elif event == 'Settings':
            filmdata_window.close()
            settings_window()
            filmdata_window = make_filmdata_window(my_title, my_desc, my_file_type, False)
            continue
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
            my_sd_filename = Path(values['FDloc'])
            sd_with_lenses_path = my_sd_filename.with_suffix('.wld')
            config.set('NikonFData', 'path', values['FDloc'])
            config.set('NikonFDataLenses', 'path', str(sd_with_lenses_path))
            with open(path_to_config, 'w') as iconfigfile:
                config.write(iconfigfile)
                iconfigfile.close()
            film_lens_chooser = make_lens_chooser_window(my_sd_filename)
            while True:
                fevent, fvalues = film_lens_chooser.Read()
                if fevent == 'Cancel' or fevent == sg.WIN_CLOSED:
                    film_lens_chooser.close()
                    film_lens_chooser_active = False
                    filmdata_window.un_hide()
                    break
                elif fevent == 'Save':
                    ISO, sd_data_db = sd_data_read(my_sd_filename)
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