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

def SPOINT(x, y):
    """Coordinate points are converted to floating point numbers""" 
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y))

def get_selected_blocks():
    # Initialize AutoCAD application
    pyacad = Autocad(create_if_not_exists=True)
    # Prompt user to select objects
    selected_objects = pyacad.get_selection()
    # Check if any objects were selected
    blocks_id = []
    if selected_objects:
        for obj in selected_objects:
            if hasattr(obj, "ObjectName") and obj.ObjectName == "AcDbBlockReference": # and obj.Name == specific_block_name:
                blocks_id.append(obj.ObjectID)
    return blocks_id

class DwgToPdf:

    def __init__(self):
        # Start AutoCAD
        self.acad = win32com.client.Dispatch("AutoCAD.Application")
        self.acad.Visible = True

        # Get the active document
        self.doc = self.acad.ActiveDocument
        self.model_space = self.doc.ModelSpace

        # # Iterate through block references in model space

        self.dwg_name = self.doc.Name
        self.dwg_prefix = self.doc.Path

        # # Initialize AutoCAD
        # acad = Autocad(create_if_not_exists=True)



    def get_blocks_by_name(self, name):
        """Retrieve all blocks with the specified name."""
        return [obj for obj in self.model_space if obj.ObjectName == "AcDbBlockReference" and obj.Name == name]


    def plot_block_to_pdf(
            self,
            block_id,
            pdf_file,
            way=2,
            config_name: str="DWG To PDF.pc3",
            stylesheet: str="monochrome.ctb",
            paper_size: str="ISO full bleed A3 (420.00 x 297.00 MM)",
            orientation: str="Landscape",
            ):
        """Plot the specified block to a PDF file."""
        block = self.doc.ObjectIdToObject(block_id)

        # Delete existing PDF file if it exists
        if os.path.isfile(pdf_file):
            os.remove(pdf_file)

        # Get bounding box
        min_point, max_point = block.GetBoundingBox()

        # First Way - Optimized
        if way == 1:
            plot_oriontation = 0 if orientation == "Landscape" else 1
            layout = self.doc.ActiveLayout
            # Set plot configuration once
            layout.ConfigName = config_name
            layout.CanonicalMediaName = paper_size
            layout.PaperUnits = 1
            layout.UseStandardScale = False
            layout.SetCustomScale(1, 1)
            layout.CenterPlot = True
            layout.PlotRotation = plot_oriontation
            layout.StyleSheet = stylesheet
            layout.PlotType = 4
            layout.StandardScale = 0
            P1 = SPOINT(*min_point[:-1])
            P2 = SPOINT(*max_point[:-1])
            layout.SetWindowToPlot(P1, P2)
            self.doc.Plot.PlotToFile(pdf_file)
            # Reduced sleep time
            time.sleep(0.1)


        # Command to plot
        # Construct the command string
        if way == 2:
                # Ensure path uses forward slashes and is quoted (handles spaces)
                safe_path = str(pdf_file).replace('\\', '/')
                quoted_path = f'"{safe_path}"'

                # Build a command-line (note leading '-' to use command-line version)
                command_lines = [
                    "-plot", "Y",        # use command-line plot
                    "Model",             # layout name (or "Layout1" as needed)
                    config_name,         # printer/pc3
                    paper_size,          # canonical media name
                    "Millimeters",       # units
                    orientation.upper(), # orientation (LANDSCAPE/PORTAIT)
                    "No",                # plot area (No -> next will be Window)
                    "Window",
                    f"{min_point[0]},{min_point[1]}",
                    f"{max_point[0]},{max_point[1]}",
                    "Fit",
                    "Center",
                    "Y",                 # plot to file? yes
                    stylesheet or "",    # plot style (may be empty)
                    "yes",               # plot with lineweight
                    "A",                 # plot what? (A = All)
                    quoted_path,         # output filename
                    "Y",                 # overwrite
                    "Y",                 # proceed
                ]

                # Join with newlines and ensure final newline so AutoCAD processes it
                command = "\n".join(command_lines) + "\n"

                    # SendCommand is asynchronous. Using SendCommand is unavoidable for some versions,
                    # but we at least avoid the file dialog by FILEDIA=0 and supplying the filename.
                self.doc.SendCommand(command)

    def export_dwg_to_pdf(
            self,
            horizontal: str="left",
            vertical: str="up", 
            prefer_dir: str='vertical',
            remove_pdfs: bool=True,
            way=2,
            config_name: str="DWG To PDF.pc3",
            stylesheet: str="monochrome.ctb",
            paper_size: str="ISO full bleed A3 (420.00 x 297.00 MM)",
            blocks_id=None,
            orientation: str="Landscape",
            ):
        """Main function to automate the PDF conversion."""
        # block_name = "kadr"
        if blocks_id is None:
            blocks_id = get_selected_blocks()
        if len(blocks_id) == 0:
            return None
        # blocks = get_blocks_by_name(block_name)
        block_boundbox = {}
        for block_id in blocks_id:
            block = self.doc.ObjectIdToObject(block_id)
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
        os.chdir(self.dwg_prefix)
        pdf_files = []
        if way == 1:
            self.doc.Plot.QuietErrorMode = False
            self.doc.SetVariable('BACKGROUNDPLOT', 0)
            # doc.Regen(1)
        elif way == 2:
            # Disable file dialogs so AutoCAD accepts the filename from the command line
            try:
                # save and disable FILEDIA (we can't always read original reliably across versions,
                # so default restore to 1)
                self.doc.SetVariable('FILEDIA', 0)
                for index, block_id in enumerate(sorted_block_id_boundbox, start=1):
                    pdf_file = str(Path(self.dwg_prefix) / f"{index}.pdf")
                    self.plot_block_to_pdf(
                        block_id,
                        pdf_file,
                        way=way,
                        config_name=config_name,
                        stylesheet=stylesheet,
                        paper_size=paper_size,
                        orientation=orientation,
                        )
                    pdf_files.append(pdf_file)
            except Exception:
                pass
            finally:
                # restore FILEDIA to 1 (safe default)
                try:
                    self.doc.SetVariable('FILEDIA', 1)
                except Exception:
                    pass
            
        pdf_name = self.doc.FullName[:-4] + '.pdf'
        if os.path.isfile(pdf_name):
            os.remove(pdf_name)
            
        # Use a context manager for file handling
        with open(pdf_name, 'wb') as output_stream:
            pdf_cat(pdf_files, output_stream)

        # Clean up temporary files
        if remove_pdfs:
            for pdf_file in pdf_files:
                try:
                    os.remove(pdf_file)
                except OSError:
                    continue

        return pdf_name


if __name__ == '__main__':
    export_dwg_to_pdf()