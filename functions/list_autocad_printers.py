import win32com.client
import win32print
import glob
import os
from pathlib import Path
from functools import lru_cache


def list_windows_printers():
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    return [info[2] for info in win32print.EnumPrinters(flags)]


def list_autocad_plot_devices1(acad=None):
    """
    Try to get plot devices from AutoCAD COM API first. If that yields nothing,
    search support paths and common AutoCAD folders for .pc3 files and return
    their base names (e.g. "DWG To PDF.pc3").
    """
    devices = []
    try:
        if acad is None:
            acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = getattr(acad, "ActiveDocument", None)
        plot_owner = None
        if doc is not None and hasattr(doc, "Plot"):
            plot_owner = doc.Plot
        elif hasattr(acad, "Plot"):
            plot_owner = acad.Plot

        if plot_owner is not None:
            for name in ("GetPlotDeviceList", "GetPlotDevices", "GetDevices"):
                if hasattr(plot_owner, name):
                    try:
                        devs = getattr(plot_owner, name)()
                        if devs:
                            # devs may be a VARIANT/tuple/COM collection
                            try:
                                devices = list(devs)
                            except Exception:
                                # try iterating
                                devices = [d for d in devs]
                            if devices:
                                return devices
                    except Exception:
                        continue
    except Exception:
        pass

    # Fallback: search for .pc3 files in support paths and common folders
    search_roots = set()

    try:
        prefs = acad.Preferences
        support = getattr(prefs.Files, "SupportFileSearchPath", None)
        if support:
            for p in support.split(';'):
                p = p.strip()
                if p:
                    search_roots.add(p)
    except Exception:
        pass

    # try acad.Path (installation folder) and common folders
    try:
        acad_path = getattr(acad, "Path", None)
        if acad_path:
            search_roots.add(os.path.join(acad_path, "Plotters"))
            search_roots.add(os.path.join(acad_path, "Support"))
    except Exception:
        pass

    for env in ("APPDATA", "LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)", "USERPROFILE"):
        val = os.environ.get(env)
        if val:
            search_roots.add(val)

    pc3_files = set()
    for root in list(search_roots):
        if not root:
            continue
        # search recursively for .pc3
        try:
            pattern = os.path.join(root, "**", "*.pc3")
            for f in glob.glob(pattern, recursive=True):
                pc3_files.add(os.path.basename(f))
        except Exception:
            continue

    return sorted(pc3_files) if pc3_files else {"windows_printers": list_windows_printers() if 'list_windows_printers' in globals() else []}
# ...existing code...

def list_autocad_plot_devices2():
    acad = win32com.client.Dispatch("AutoCAD.Application")
    doc = acad.ActiveDocument
    # Try the common Plot API call (may vary by AutoCAD version)
    try:
        devices = doc.Plot.GetPlotDeviceList()
        return list(devices)
    except Exception:
        # Try some alternative method names that appear in different versions
        for name in ("GetPlotDeviceList", "GetPlotDevices", "GetDevices"):
            try:
                if hasattr(doc.Plot, name):
                    devices = getattr(doc.Plot, name)()
                    return list(devices)
            except Exception:
                pass
    # Fallback: return Windows printers and try to discover .pc3 files in support paths
    printers = list_windows_printers()
    # try to find PC3 files in AutoCAD support paths (best-effort)
    pc3_names = []
    try:
        # SupportFileSearchPath often contains semicolon-separated folders
        support_paths = acad.Preferences.Files.SupportFileSearchPath
        if isinstance(support_paths, str):
            for p in support_paths.split(';'):
                p = p.strip()
                if p:
                    pc3_names += [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(p, "*.pc3"))]
    except Exception:
        pass
    return {"windows_printers": printers, "pc3_devices": pc3_names}


@lru_cache(maxsize=1)
def list_autocad_plot_devices(acad=None):
    """Get plot devices from AutoCAD with caching for better performance."""
    devices = set()
    
    # Try direct COM API first (fastest)
    try:
        if acad is None:
            acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.ActiveDocument
        if hasattr(doc.Plot, "GetPlotDeviceList"):
            return list(doc.Plot.GetPlotDeviceList())
    except Exception:
        pass

    # Quick search in common AutoCAD paths
    common_paths = [
        Path(os.environ.get('USERPROFILE', '')) / "AppData/Roaming/Autodesk/AutoCAD/Plot Configs",
        Path(os.environ.get('ProgramFiles', '')) / "Autodesk/AutoCAD/Plotters",
        Path(os.environ.get('ProgramFiles(x86)', '')) / "Autodesk/AutoCAD/Plotters",
    ]

    # Add AutoCAD support paths if available
    try:
        if acad and hasattr(acad.Preferences.Files, "PrinterConfigPath"):
            common_paths.append(Path(acad.Preferences.Files.PrinterConfigPath))
        if acad and hasattr(acad.Preferences.Files, "PrinterDescPath"):
            common_paths.append(Path(acad.Preferences.Files.PrinterDescPath))
    except Exception:
        pass

    # Fast PC3 file search
    for path in common_paths:
        if path.exists():
            devices.update(f.name for f in path.glob("*.pc3"))
            # Stop after finding files in any path
            if devices:
                break

    return sorted(devices) if devices else ["DWG To PDF.pc3"]  # Return default if nothing found


@lru_cache(maxsize=1)
def get_autocad_plot_resources(acad=None):
    """Get plot devices and plot styles from AutoCAD with caching."""
    try:
        if acad is None:
            acad = win32com.client.Dispatch("AutoCAD.Application")
        
        plot_styles = set()
          
        # Get plot style paths from AutoCAD preferences
        style_paths = []
        try:
            style_paths.append(Path(acad.Preferences.Files.PrinterStyleSheetPath))
        except:
            pass
            
        # Common paths for plot styles
        common_paths = [
            Path(os.environ.get('USERPROFILE', '')) / "AppData/Roaming/Autodesk/AutoCAD/Plot Styles",
            Path(os.environ.get('ProgramFiles', '')) / "Autodesk/AutoCAD/Plot Styles",
            Path(os.environ.get('ProgramFiles(x86)', '')) / "Autodesk/AutoCAD/Plot Styles",
            *style_paths
        ]

        # Fast file search
        for path in common_paths:
            if path and path.exists():
                # Get both color-dependent (CTB) and named (STB) plot styles
                plot_styles.update(f.name for f in path.glob("*.ct*"))  # Color tables
                plot_styles.update(f.name for f in path.glob("*.st*"))  # Named tables
                if plot_styles:
                    break

        return sorted(plot_styles) if plot_styles else ["monochrome.ctb", "acad.ctb"]
        
    except Exception as e:
        print(f"Error getting plot resources: {e}")
        return ["monochrome.ctb", "acad.ctb"]
    
from functools import lru_cache
import win32com.client

@lru_cache(maxsize=1)
def get_printer_media_names(device, acad=None):
    """Get available media names (paper sizes) for each plot device."""
    try:
        if acad is None:
            acad = win32com.client.Dispatch("AutoCAD.Application")
        
        doc = acad.ActiveDocument
        layout = doc.ActiveLayout
        layout.ConfigName = device
        try:
            media_names = list(layout.GetCanonicalMediaNames())
        except Exception as e:
            print(f"Error getting media names for {device}: {e}")
            media_names = []        
        return media_names

    except Exception as e:
        print(f"Error accessing AutoCAD: {e}")
        return []

# Example usage
if __name__ == "__main__":
    media_names = get_printer_media_names()
    for printer, media in media_names.items():
        print(f"\nPrinter: {printer}")
        print("Available paper sizes:")
        for name in media:
            print(f"- {name}")

if __name__ == "__main__":
    print("AutoCAD plot devices (or fallback):")
    print(list_autocad_plot_devices())
    print("\nWindows printers:")
    print(list_windows_printers())

    # resources = get_autocad_plot_resources()
    # print("\nPlot Styles:")
    # for style in resources:
    #     print(f"- {style}")