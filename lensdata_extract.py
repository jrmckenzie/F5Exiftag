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

# OK so if you want to try and use these scripts for tagging lens data be warned this is
# messy, not user-friendly and instructions are poor.
#
# There is some initial setup to be done once to build EXIF profiles of each of
# your Nikon lenses.
#
# Using a Nikon DSLR, shoot one photograph with each of your AF lenses and your AI-P lenses
# (by AI-P we mean manual focus lenses with CPU such as Voigtlander SL-II, Zeiss ZF.2,
# Samyang etc). Set the camera to Manual and shoot them at a high shutter speed with the
# lens cap on so the embedded thumbnails will be black. Make sure the camera will save
# the shots in JPG format.
#
# Then create a subdirectory of your Nikon directory named "Lenses" and # copy the JPG of
# each of those photos from the camera's memory card to there. These will serve as
# templates for the EXIF metadata for the images tagged with a particular lens by this
# utility. Say you have created a "Nikon" directory inside your Documents directory. The
# "Nikon" directory should have two subdirectories: "Lenses" and "Shooting Data". You put
# your lens JPGs in "Lenses" and your Shooting Data .txt files in "Shooting Data".
#
# Documents/
# ├─ Nikon/
# │  ├─ Lenses/
# │  ├─ Shooting Data/
#
# Now you've got that setup it's time to run this script. It will create a small csv
# file which will contain details of the name, focal length and location of the
# reference JPG image of each of the lenses in your collection. You won't need to
# run lensdata_extract.py again unless you have a new lens to add to your collection
# or if you delete the F5Exiftag directory containing this script and its
# sub-directory named lens_tagging.
#
# Once this setup is done you can use the lens_chooser.py script to associate every
# image on your scanned film roll with one of your lenses and then run
# lens_tag_writer.py to actually tag your scans.
#
# What will happen ultimately is that all the EXIF data in the DSLR-shot JPG will be
# copied to the scanned image from your F5 film roll. Then the camera model (NIKON F5),
# shutter speed, aperture and film speed ISO from the F5 shooting data will overwrite
# the DSLR's metadata for these items only. Yes it's messy and all the rest of the
# DSLR's own metadata will remain. Including date and time. Unless you've been using
# the MF-28 multifunction back with the F5 and configured it to save date and time
# into the shooting data. You're probably better using something like Lenstagger from
# https://www.lenstagger.com/ if you can. Much easier.
#
# This script doesn't have a GUI. You just run it in the console / command line.

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
pathlist = image_dir.rglob('*.JPG')
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