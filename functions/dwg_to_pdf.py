import os
import sys
from pathlib import Path
import time

try:
    import win32com.client
except ImportError:
    package = 'pypiwin32'
    from freecad_funcs import install_package
    install_package(package_name=package)
import win32com.client

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    package = 'pypdf'
    from freecad_funcs import install_package
    install_package(package_name=package)

from pypdf import PdfReader, PdfWriter

try:
    from pyautocad import Autocad
except ImportError:
    package = 'pyautocad'
    from freecad_funcs import install_package
    install_package(package_name=package)
from pyautocad import Autocad

try:
    import pythoncom
except ImportError:
    package = 'pythoncom'
    from freecad_funcs import install_package
    install_package(package_name=package)
import pythoncom

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))

# Start AutoCAD
acad = win32com.client.Dispatch("AutoCAD.Application")
acad.Visible = True

# Get the active document
doc = acad.ActiveDocument
model_space = doc.ModelSpace

# # Iterate through block references in model space

dwg_name = doc.Name
dwg_prefix = doc.Path

# # Initialize AutoCAD
# acad = Autocad(create_if_not_exists=True)


def pdf_cat(input_files, output_stream):
    # pdf_name = sys.stdout
    input_streams = []
    try:
        # First open all the files, then produce the output file, and
        # finally close the input files. This is necessary because
        # the data isn't read from the input files until the write
        # operation. Thanks to
        # https://stackoverflow.com/questions/6773631/problem-with-closing-python-pypdf-writing-getting-a-valueerror-i-o-operation/6773733#6773733
        for input_file in input_files:
            input_streams.append(open(input_file, 'rb'))
        writer = PdfWriter()
        for reader in map(PdfReader, input_streams):
            for n in range(len(reader.pages)):
                writer.add_page(reader.pages[n])
        writer.write(output_stream)
    finally:
        for f in input_streams:
            f.close()
        writer.close()

def get_blocks_by_name(name):
    """Retrieve all blocks with the specified name."""
    return [obj for obj in model_space if obj.ObjectName == "AcDbBlockReference" and obj.Name == name]

def SPOINT(x, y):
    """Coordinate points are converted to floating point numbers""" 
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y))

def plot_block_to_pdf(block_id, pdf_file, way=1):
    """Plot the specified block to a PDF file."""
    block = doc.ObjectIdToObject(block_id)

    # Delete existing PDF file if it exists
    if os.path.isfile(pdf_file):
        os.remove(pdf_file)

    # Get bounding box
    min_point, max_point = block.GetBoundingBox()

    # First Way
    if way == 1:
        P1=SPOINT(*min_point[:-1])
        P2=SPOINT(*max_point[:-1])
        doc.ActiveLayout.SetWindowToPlot(P1,P2)
        doc.Plot.PlotToFile(pdf_file) #nombre del fichero donde se va imprimir
        time.sleep(.1)


    # Command to plot
    # Construct the command string
    if way == 2:
        command = (
            '-plot Y\n'  # Plotting option
            'Model\n'  # Layout name
            'DWG To PDF.pc3\n'  # Printer name
            'ISO full bleed A3 (420.00 x 297.00 MM)\n'  # Paper size
            'Millimeters\n'  # Units
            'LANDSCAPE\n'  # Orientation
            'No\n'  # Window option
            'Window\n'  # Window option
            f'{min_point[0]},{min_point[1]}\n'  # Plot area
            f'{max_point[0]},{max_point[1]}\n'  # Plot area
            'Fit\n'  # Scale option
            'Center\n'  # Centering option
            'Y\n'  # Plot to file
            'monochrome.ctb\n' # Plot style file
            'yes\n' # plot with lineweight
            'A\n'
            f'{pdf_file}\n'  # Output file
            'Y\n'  # Overwrite option
            'Y\n' # proceed with plot
        )
        # Send the command to AutoCAD
        doc.SendCommand(command)

def export_dwg_to_pdf(
        horizontal: str="left",
        vertical: str="up",
        prefer_dir: str='vertical',
        remove_pdfs: bool=True,
        way=1,
        ):
    """Main function to automate the PDF conversion."""
    # block_name = "kadr"


    # Initialize AutoCAD application
    pyacad = Autocad(create_if_not_exists=True)

    # Prompt user to select objects
    selected_objects = pyacad.get_selection()


    # Check if any objects were selected
    if selected_objects:
        blocks_id = []

        for obj in selected_objects:
            if hasattr(obj, "ObjectName") and obj.ObjectName == "AcDbBlockReference": # and obj.Name == specific_block_name:
                blocks_id.append(obj.ObjectID)
    else:
        return None
    # blocks = get_blocks_by_name(block_name)
    block_boundbox = {}
    for block_id in blocks_id:
        block = doc.ObjectIdToObject(block_id)
        min_point, max_point = block.GetBoundingBox()
        block_boundbox[block.ObjectID] = min_point
    # Sort keys based on (x, -y) to sort y in descending order when x is the same
    # Determine sign for x and y based on the direction
    x_sign = 1 if horizontal == "right" else -1
    y_sign = -1 if vertical == "down" else 1
    if prefer_dir == "vertical":
        sorted_block_id_boundbox = sorted(block_boundbox.keys(), key=lambda k: (x_sign * int(block_boundbox[k][0]), y_sign * block_boundbox[k][1]))
    else:
        sorted_block_id_boundbox = sorted(block_boundbox.keys(), key=lambda k: (y_sign * int(block_boundbox[k][1]), x_sign * block_boundbox[k][0]))
    # change the path
    dwg_prefix = doc.Path
    os.chdir(dwg_prefix)
    pdf_files = []
    if way == 1:
        doc.ActiveLayout.ConfigName= "DWG To PDF.pc3"  #se puede cambiar a cualquier pc3 configurado
        doc.ActiveLayout.CanonicalMediaName = "ISO_expand_A4_(297.00_x_210.00_MM)" #debe coincidir exctamente el nombre 
        doc.ActiveLayout.PaperUnits = 1
        doc.ActiveLayout.CenterPlot = True
        doc.Plot.QuietErrorMode = False
        doc.ActiveLayout.UseStandardScale = False
        doc.ActiveLayout.SetCustomScale(1, 1) #escala del dibujo
        doc.SetVariable('BACKGROUNDPLOT', 0)
        doc.Regen(1)
        doc.ActiveLayout.CenterPlot = True
        doc.ActiveLayout.PlotRotation = 0
        doc.ActiveLayout.StyleSheet = "monochrome.ctb" #plantilla de plumillas
        doc.ActiveLayout.PlotType = 4 #acWindow
        doc.ActiveLayout.StandardScale = 0 #acScaleToFit

    for index, block_id in enumerate(sorted_block_id_boundbox, start=1):
        pdf_file = str(Path(dwg_prefix) / f"{index}.pdf")
        plot_block_to_pdf(block_id, pdf_file, way=way)
        pdf_files.append(pdf_file)
        
    pdf_name = doc.FullName[:-4] + '.pdf'
    if os.path.isfile(pdf_name):
        os.remove(pdf_name)
    print(pdf_name)
    pdf_cat(pdf_files, pdf_name)

    if remove_pdfs:
        for pdf_file in pdf_files:
            if os.path.isfile(pdf_file):
                os.remove(pdf_file)
    return pdf_name


if __name__ == '__main__':
    export_dwg_to_pdf()