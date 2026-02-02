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
from pyautocad import Autocad, APoint

try:
    import pythoncom
except ImportError:
    package = 'pythoncom'
    from freecad_funcs import install_package
    install_package(package_name=package)
import pythoncom

civiltools_path = Path(__file__).parent.parent
sys.path.insert(0, str(civiltools_path))

import civiltools_python_functions as cpf


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

    def __init__(self, block_ids=None):
        # Start AutoCAD
        self.acad = win32com.client.Dispatch("AutoCAD.Application")
        self.acad.Visible = True
        self.block_ids = block_ids
        # Get the active document
        self.get_doc_according_to_drawing_name()

    def get_doc_according_to_drawing_name(self, target_drawing_name=None):
        self.doc = None
        if target_drawing_name is None:
            self.doc = self.acad.ActiveDocument
        else:
            # Search through all open documents
            for doc in self.acad.Documents:
                if doc.Name == target_drawing_name:
                    self.doc = doc
                    self.doc.Activate()
                    break
        if self.doc is not None:
            print(f"Found drawing: {self.doc.Name}")
            self.dwg_name = self.doc.Name
            self.dwg_prefix = self.doc.Path
            if hasattr(self.doc, 'FullName'):
                self.full_name = self.doc.FullName
            else:
                self.full_name = None
        else:
            print(f"Drawing '{target_drawing_name}' not found in open documents.")

    def get_all_open_drawing_names(self):
        # List all open documents
        return [doc.Name for doc in self.acad.Documents]
    
    def get_all_block_definitions(self): # -> List[str]:
        """Get all block definition names in the drawing"""
        try:
            block_names = []
            block_table = self.doc.Database.Blocks
            
            for block in block_table:
                # Skip *Model_Space, *Paper_Space, and layouts
                if not block.Name.startswith('*') and not block.IsLayout:
                    block_names.append(block.Name)
            
            print(f"Found {len(block_names)} block definitions")
            return block_names
            
        except Exception as e:
            print(f"Error getting block definitions: {e}")
            return []
        
    def get_all_blocks_probable_to_be_sheet(self):
        block_names = self.get_all_block_definitions()
        for b_name in block_names:
            block = self.doc

    def get_selected_blocks(self):
        """
        Prompt user to select objects using the SelectionSets API.
        Returns a list of block ObjectIDs.
        """
        block_ids = []
        selection_name = "Temp_Selection"

        try:
            # Get the SelectionSets collection
            selection_sets = self.doc.SelectionSets

            # Delete the temporary selection set if it already exists
            for i in range(selection_sets.Count):
                if selection_sets.Item(i).Name == selection_name:
                    selection_sets.Item(i).Delete()
                    break

            # Create a new, empty selection set
            selection = selection_sets.Add(selection_name)

            # Let the user select objects on screen
            print("Please select blocks in the drawing and press Enter...")
            selection.SelectOnScreen()  # This waits for user input

            # Process the selected objects
            for i in range(selection.Count):
                obj = selection.Item(i)
                if obj.ObjectName == "AcDbBlockReference":
                    block_ids.append(obj.ObjectID)

            # Clean up the selection set
            selection.Delete()

        except Exception as e:
            print(f"Selection error: {e}")
            # Ensure cleanup even if an error occurs
            try:
                self.doc.SelectionSets.Item(selection_name).Delete()
            except:
                pass
        self.block_ids = block_ids
        return block_ids
    
    def select_block_by_name(self, block_name: str):
        """Select all instances of a block by name in model space"""
        try:
            # Switch to model space
            self.doc.ActiveLayout = self.doc.Layouts.Item("Model")
            
            # Create selection set
            selection_sets = self.doc.SelectionSets
            temp_ss_name = f"TempSelect_{int(time.time())}"
            
            # Delete if exists
            for i in range(selection_sets.Count):
                if selection_sets.Item(i).Name == temp_ss_name:
                    selection_sets.Item(i).Delete()
                    break
            
            # Create new selection set
            ss = selection_sets.Add(temp_ss_name)
            
            # Filter for block references with specific name
            filter_types = [2] # Block name filter type
            filter_values = [block_name]
            filter_types.append(0)  # Entity type
            filter_values.append("INSERT")
            filter_type_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, filter_types)
            filter_data_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, filter_values)
            
            # First select all block references
            # Select all with filter
            ss.Select(5, None, None, filter_type_array, filter_data_array)
            
            # Get selected blocks
            block_ids = []
            for i in range(ss.Count):
                block = ss.Item(i)
                block_ids.append(block.ObjectID)
            
            # Clear selection set
            ss.Delete()
            
            if block_ids:
                print(f"Selected {len(block_ids)} instances of block '{block_name}'")
            else:
                print(f"No instances found for block '{block_name}'")
            
        except Exception as e:
            print(f"Error selecting block {block_name}: {e}")
        self.block_ids = block_ids
        return block_ids

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

    def sort_blocks(self,
            horizontal: str="left",
            vertical: str="up", 
            prefer_dir: str='vertical',
    ):
        if isinstance(self.block_ids, list) and len(self.block_ids) > 0:
            block_boundbox = {}
            for block_id in self.block_ids:
                block = self.doc.ObjectIdToObject(block_id)
                min_point, max_point = block.GetBoundingBox()
                x1, y1 = min_point[0], min_point[1]
                x2, y2 = max_point[0], max_point[1]
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                # min_point = []
                block_boundbox[block.ObjectID] = min_point
            # Sort keys based on (x, -y) to sort y in descending order when x is the same
            # Determine sign for x and y based on the direction
            x_sign = 1 if horizontal == "right" else -1
            y_sign = -1 if vertical == "down" else 1
            if prefer_dir == "vertical":
                sorted_block_id_boundbox = sorted(block_boundbox.keys(), key=lambda k: (x_sign * int(block_boundbox[k][0]), y_sign * block_boundbox[k][1]))
            else:
                sorted_block_id_boundbox = sorted(block_boundbox.keys(), key=lambda k: (y_sign * int(block_boundbox[k][1]), x_sign * block_boundbox[k][0]))

        return sorted_block_id_boundbox

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
            orientation: str="Landscape",
            ):
        """Main function to automate the PDF conversion."""
        if len(self.block_ids) == 0:
            return None
        block_ids = self.sort_blocks(horizontal, vertical, prefer_dir)
        print(f"{block_ids=}")
        
        # change the path
        os.chdir(self.dwg_prefix)
        pdf_files = []
        if way == 1:
            self.doc.Plot.QuietErrorMode = False
            self.doc.SetVariable('BACKGROUNDPLOT', 0)
            for index, block_id in enumerate(block_ids, start=1):
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
            # doc.Regen(1)
        elif way == 2:
            # Disable file dialogs so AutoCAD accepts the filename from the command line
            try:
                # save and disable FILEDIA (we can't always read original reliably across versions,
                # so default restore to 1)
                self.doc.SetVariable('FILEDIA', 0)
                for index, block_id in enumerate(block_ids, start=1):
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
        if self.full_name:
            pdf_name = self.full_name[:-4] + '.pdf'
        else:
            pdf_name = cpf.get_temp_filepath('pdf', 'civiltools_plot_to_dwg')
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
    
    def add_and_number_attributes(self,
                                    horizontal: str="left",
                                    vertical: str="up", 
                                    prefer_dir: str='vertical',
                                    block_ids=None,
                                    attribute_tag="SHEET_NO",
                                    ):
        """Add attributes to blocks and number them sequentially"""
        if block_ids is None:
            block_ids = self.sort_blocks(horizontal, vertical, prefer_dir)
        for i, block_id in enumerate(block_ids):
            block = self.doc.ObjectIdToObject(block_id)
            block_name = block.Name
            
            # Check if block has attributes
            if block.HasAttributes:
                attrs = block.GetAttributes()
                attribute_found = False
                
                # Look for existing attribute
                for attr in attrs:
                    if attr.TagString == attribute_tag:
                        attr.TextString = str(i + 1)
                        attr.Update()
                        attribute_found = True
                        print(f"Updated {attribute_tag} to {i+1} in block {block_name}")
                        break
                
                # If attribute doesn't exist, add it to the block definition
                if not attribute_found:
                    self._add_attribute_to_definition(block_name, attribute_tag, i+1, block)
            else:
                # Block has no attributes at all
                self._add_attribute_to_definition(block_name, attribute_tag, i+1, block)
        return i+1
    
    def _add_attribute_to_definition(self, block_name, attribute_tag, number, block_instance):
        """Add attribute to block definition and update instance"""
        try:
            # Access block definition
            block_def = self.doc.Blocks.Item(block_name)
            
            # Define attribute position relative to block insertion point
            # You can adjust these coordinates based on your needs
            insert_point = block_instance.InsertionPoint
            attr_position = (insert_point[0] + 5, insert_point[1] + 5, insert_point[2])
            
            # Add attribute definition to block
            attr_def = block_def.AddAttribute(
                2.5,  # Text height
                0,    # Mode (0=visible, editable)
                "Sheet Number:",  # Prompt
                attr_position,    # Insertion point
                attribute_tag,    # Tag
                str(number)       # Default value
            )
            
            # Sync attributes to update all instances
            self.doc.SendCommand(f"_-ATTSYNC _N {block_name} ")
            print(f"Added {attribute_tag} attribute to block {block_name} with value {number}")
            
        except Exception as e:
            print(f"Error adding attribute to {block_name}: {e}")
            # Fallback: add text near the block if attribute fails
            self._add_text_as_fallback(block_instance, number)
    
    def _add_text_as_fallback(self, block, number):
        """Add plain text as fallback if attribute creation fails"""
        try:
            insert_point = block.InsertionPoint
            text_point = APoint(insert_point[0] + 5, insert_point[1] + 5)
            
            # Use pyautocad for text creation (if available)
            from pyautocad import Autocad
            pyacad = Autocad(create_if_not_exists=True)
            text = pyacad.model.AddText(str(number), text_point, 2.5)
            text.Layer = "SHEET_NUMBERS"
            print(f"Added text {number} near block as fallback")
        except:
            print(f"Could not add text near block {block.ObjectID}")


if __name__ == '__main__':
    export_dwg_to_pdf()