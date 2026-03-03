F5Exiftag
=========

This is a tool for Nikon F5 camera users who connect their camera to a PC or Mac with a serial cable and use Nikon Photo Secretary for F5 to save the Shooting Data from a roll of film. If you have a saved Shooting Data file for a roll of film and a corresponding set of digital scans of each frame in the film, this tool will tag each scanned image with EXIF data corresponding to the information in the Shooting Data. If those images are then uploaded to sites like flickr.com then the EXIF-based data (where it shows the make and model of camera, lens, exposure etc.) will correspond to the F5 shooting data and not just the digital scan.
Hardware requirements to do this are a Nikon F5 film camera, a Nikon MC-31 or MC-33 connecting cord (or DIY equivalent), and an RS232 serial to USB converter cable to interface between Nikon's cable and a USB port (the latter is needed unless you have a PC with physical COM ports). 

Software requirements are [Nikon AC-1WE Photo Secretary for F5](https://cdn-10.nikon-cdn.com/pdf/manuals/archive/AC-1WE%20Photo%20Secretary%20for%20F5.pdf) (for Windows 95) which dates back to 1997 but copies can be found online and made to run under Windows 11 and Linux with a moderate amount of tweaking.

This python script requires the packages [FreeSimpleGUI](https://pypi.org/project/FreeSimpleGUI/) and [PyExifTool](https://pypi.org/project/PyExifTool/). Install them with pip. PyExifTool is a wrapper for [ExifTool](https://exiftool.org/) so make sure you have that installed too.

To do, maybe
============

Compatibility with the data files output by [Nikon AC-2WE Photo Secretary for F100](https://cdn-10.nikon-cdn.com/pdf/manuals/archive/AC-2WE%20Photo%20Secretary%20II%20for%20F100%20-%20Windows.pdf) and [SoftTALK-2000](https://www.cocoon-creations.com/COCOON-NiCommSoftTALK-98.shtml). This would bring compatibility with Nikon F90x and F100. Should be pretty easy to do.

Donations
=========

Are welcome via https://ko-fi.com/jzmck
