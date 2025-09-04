# Rapid Image Annotator

This folder contains files associated with version 2.6.10 of the Rapid Image Annotator

## Using the image annotator:
After downloading the entire RIA folder, run RIA.exe
Load an image directory using the “load image directory” button
Load the annotation file using the “load data directory” button (defaults to data/annotations.json in the local directory)
Use the “settings” button to change the annotator color schemes and keybindings
Key inputs will not work when hovering mouse over the toolbar

## Default keybindings:
 * left/right arrows: change image
 * spacebar: clear boxes
 * enter: save boxes
 * backspace/delete: delete selected box
 * page up/ page down/ mouse-over: select a box
 * wasd & WASD (using shift + key): change box shape, wasd moves the top and right margins, WASD moves the bottom and left margins
 * z key: toggle zoom
 * Left mouse button: click and drag to draw box
 * Right mouse button: save data and move to next image

All keybindings can be modified, although issues may arrise when setting multiple functions to the same key. 
Additionally, set comments can be bound to keys, which will store text associated with a specific bounding box or the entire image, depending on selection.

Annotations will be saved as a json with keys representing each image, and items representing the bounding boxes / circles / lines set in each image in x1,y1,x2,y2 format.

## Version 2.6.10
### Feature additions
    - Made filename display generic to tasks
    - Made text displaying annotation times more readable
    - Improved box selection and deselection
    - General aesthetic improvements

### Bug fixes

    - Made box comments less likely to fall outside image 
    - Prevented binding of mouse buttons to simultaneous image navigation and comments
    - Allowed saving of zero width / height boxes
    - Prevented pagination from accidently overwriting annotations
    - Eliminated edge case where new boxes could overwrite old box data 

### License: GNU Affero General Public License v3.0 (2025)
