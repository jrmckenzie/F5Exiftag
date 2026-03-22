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

# Using a Nikon DSLR, shoot one photograph with each of your AF lenses and your AI-P lenses
# (by AI-P we mean manual focus lenses with CPU such as Voigtlander SL-II, Zeiss ZF.2,
# Samyang etc). Then create a subdirectory of your Nikon Shooting Data directory named
# "Lenses" and copy the JPG of each of those photos there. These will serve as templates
# for the EXIF metadata for the images tagged with a particular lens by this utility.

import sys
import configparser
from pathlib import Path
from exiftool import ExifTool
import pandas as pd
import json
from io import StringIO

from main import script_path, version_number, version_date
from lens_chooser import my_nikon_lenses_path

print(Path(__file__).name, version_number, version_date)
config = configparser.ConfigParser()
path_to_config = script_path / 'config.ini'
config.read(path_to_config)

# Read configuration and find location of Nikon Shooting Data folder, or ask user to set it
if config.has_option('NikonSData', 'path'):
    shooting_data_path = config.get('NikonSData', 'path')
else:
    sys.exit('Please run the main.py script first to configure the Nikon / Shooting Data folder, and try again.')
image_dir = Path(shooting_data_path).parent / "Lenses"
pathlist = image_dir.glob('*.JPG')
nikon_lens_db_path = script_path / "lens_tagging" / "nikon_lens_db.csv"
nikon_lens_db = pd.read_csv(nikon_lens_db_path, index_col=0)
appended_data = []
myappended_data = []
print("Processing:")
for path in pathlist:
    # because path is object not string
    path_in_str = str(path)
    print("  ", path_in_str)
    with ExifTool() as et:
        my_json = json.loads(et.execute("-j", "-MinFocalLength", "-LensID", path_in_str))
        mydf = pd.read_json(StringIO(json.dumps(my_json)), orient='records')
        my_lens_id_hex = mydf["Composite:LensID"].values.tolist()
        my_lens_id_hex = my_lens_id_hex[0]
        my_lens_id = nikon_lens_db.query('index == @my_lens_id_hex')
        my_lens = my_lens_id["LensID"].values.tolist()
        mydf.insert(3, "LensID", my_lens)
        myappended_data.append(mydf)
        appended_data = pd.concat(myappended_data)
appended_data.drop_duplicates(subset="LensID", inplace=True)
appended_data.sort_values(by=["MakerNotes:MinFocalLength"], inplace=True)
appended_data.to_csv(my_nikon_lenses_path, index=False)
print("Lens data saved in", my_nikon_lenses_path)