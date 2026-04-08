F5Exiftag
=========

This is a tool for Nikon F5 camera users who connect their camera to a PC or Mac with a serial cable and use Nikon Photo Secretary for F5 to save the Shooting Data from a roll of film. If you have a saved Shooting Data file for a roll of film and a corresponding set of digital scans of each frame in the film, this tool will tag each scanned image with EXIF data corresponding to the information in the Shooting Data. If those images are then uploaded to sites like flickr.com then the EXIF-based data (where it shows the make and model of camera, lens, exposure etc.) will correspond to the F5 shooting data and not just the digital scan.
Hardware requirements to do this are a Nikon F5 film camera, a Nikon MC-31 or MC-33 connecting cord (or DIY equivalent), and an RS232 serial to USB converter cable to interface between Nikon's cable and a USB port (the latter is needed unless you have a PC with physical COM ports). 

Software requirements are [Nikon AC-1WE Photo Secretary for F5](https://cdn-10.nikon-cdn.com/pdf/manuals/archive/AC-1WE%20Photo%20Secretary%20for%20F5.pdf) (for Windows 95) which dates back to 1997 but copies can be found online and made to run under Windows 11 and Linux with a moderate amount of tweaking. In Linux, if you are using a USB to serial cable, you may have to give the user permission to read and write to /dev/ttyUSB0 and, using wine, use regedit to map the wine COM2 port onto /dev/ttyUSB0. Once set up it works very well via wine on Linux. In contrast, setting it up on Windows 11 can be a bit tricky because the installer won't run. But if you can find a way to extract / copy all the program files and DLLs over to Windows 11 and run FilMan.exe it does work.

This python script requires the packages [pandas](https://pandas.pydata.org/), [FreeSimpleGUI](https://pypi.org/project/FreeSimpleGUI/) and [PyExifTool](https://pypi.org/project/PyExifTool/). Install them with pip. PyExifTool is a wrapper for [ExifTool](https://exiftool.org/) so make sure you have that installed and working on the command line too. This script will work on Windows or Linux.

To use it, fire up Nikon Photo Secretary for F5, connect the camera, retreive the shooting data from the camera. Make sure you export it as a .txt file because that is what will be used here. Scan each frame of the film as a jpg (yes, every frame don't skip any or the numbering may go wrong and photos could get tagged with the wrong data). There is a strict naming / filing convention here:
* You have one directory called "Nikon Shooting Data" or something like that where the shooting data is saved with the default name suggested by Nikon Photo Secretary. e.g. "2550101.txt" or something like that.
* For each roll of film you create one directory for all of the scanned images. It could be a subdirectory of Nikon Shooting Data or anywhere else you like.
* For each scanned image of that film (this is very important) you must name it EXACTLY as per the shooting data file, followed by a hyphen (minus sign) and the frame number of the film that was scanned. No leading zeroes in the frame number. No spaces. Following the above example the names would be 2550101-1.jpg, 2550101-2.jpg etc. If you're using Lightroom or something similar you can set it up to export files with this naming convention including the numbering starting at 1. 

Then run main.py. It will ask where your Nikon Shooting Data folder is then ask you to find the shooting data you want to use, and find the folder where all your scanned images are. Be sure you have backups in case it goes wrong. Then press Go and you should see a progress bar move along as the images are tagged one by one with exposure data, aperture, focal length etc. 

There are some other scripts and directories besides main.py but these are experimental bits and pieces probably best left alone. See below.

If you want it to tag the files with your camera's serial number you can press the Settings button and enter the 7 digit serial number.

Experimental, maybe don't bother trying
=======================================

Before I heard of [Lenstagger](https://www.lenstagger.com/) I wrote some hacky scripts to provide a way to select a lens and tag the scanned jpg image with the corresponding lens metadata. It was quite an involved process where you use a Nikon DSLR (yes, a DSLR) and shoot one photograph using each of your lenses then store the JPGs of those photos to act as templates for the metadata of the relevant lens. Since Lenstagger exists, probably just use that instead. The scripts lensdata_extract.py, lens_chooser.py and lens_tag_writer.py attempt to do this. It's not pretty. Lensdata_extract.py was supposed to be run just once (or whenever you get a new lens) to create a database of all your lenses. Then after you'd run main.py you could fire up lens_chooser.py and select which of your lenses each of the shots on your roll of film was taken with. Finally you could open lens_tag_writer.py and actually tag the scanned jpg images with the lens data you previously saved with lens_chooser.py. There's some more info in the comments section of the lensdata_extract.py script. But why bother with any of this when you can use the excellent and free Lenstagger, if you have Lightroom that is. I have no plans to put any more work into the lens tagging scripts.

To do, maybe
============

* Compatibility with the data files output by [Nikon AC-2WE Photo Secretary for F100](https://cdn-10.nikon-cdn.com/pdf/manuals/archive/AC-2WE%20Photo%20Secretary%20II%20for%20F100%20-%20Windows.pdf) and [SoftTALK-2000](https://www.cocoon-creations.com/COCOON-NiCommSoftTALK-98.shtml). This would bring compatibility with Nikon F90x, F100 and F6. Should be pretty easy to do. I don't have any of those cameras to be able to try it and test it.

* More in the way of documentation or code comments. Good luck trying to understand or follow any of the code. I'm no coder and don't even know how to use github properly. This repository only really exists so I can maintain copies of my own code for my own use and remind myself how to use it. And the offchance it may be of interest to someone else.

Donations
=========

Are welcome via https://ko-fi.com/jzmck as are gifts of F90x, F100 and F6 cameras in working order.
