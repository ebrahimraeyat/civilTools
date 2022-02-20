import math
from typing import Iterable, Union
import FreeCADGui as Gui
import FreeCAD, Arch
import WorkingPlane


def get_all_stories():
    '''
    return all Building Storey in ActiveDocument according to elevations
    '''
    all_stories = []
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'IfcType') and obj.IfcType == 'Building Storey':
            all_stories.append(obj)
    all_stories.sort(key=lambda s : s.Elevation.getValueAs('mm'))
    return all_stories

def get_above_beam(beam, stories):
    inlists = beam.InList
    if inlists:
        for o in inlists:
            if hasattr(o, 'IfcType') and o.IfcType == 'Building Storey':
                story = o
                break
    else:
        return None
    i_story = stories.index(story)
    if i_story == len(stories) - 1:
        return None
    label = beam.Label.split('_')[0]
    for i in range(i_story + 1, len(stories)):
        story_name = stories[i].Label
        ret_beam = FreeCAD.ActiveDocument.getObjectsByLabel(f'{label}_{story_name}')
        if not ret_beam:
            continue
        else:
            return ret_beam[0]
    return None

def add_wall_on_beams(
        loadpat : str,
        mass_per_area : float,
        dist1 : float = 0,
        dist2 : float = 1,
        labels : Union[list, bool] = None,
        stories : Union[Iterable, bool] = None,
        load_type : int = 1, # 1: Force per len , 2: Moment per len
        relative : bool = True,
        replace : bool = True,
        height : Union[float, bool] = None,
        none_beam_h : float = 0,
        parapet : float = 1100,
        # height_from_below : bool = False,
        opening_ratio : float = 0,
    ):
    if labels is None:
        sel = Gui.Selection.getSelection()
        labels = set()
        for o in sel:
            if (hasattr(o, 'IfcType') and o.IfcType == 'Beam') or (
                o.Label.startswith('B') and o.Label.endswith('CenterLine')
            ):
                label = o.Label.split('_')[0]
                labels.add(label)
    all_stories = get_all_stories()
    stories_objects = dict()
    
    if stories is None:
        stories = [s.Label for s in all_stories[1:]]
    for label in labels:
        similar_label_in_stories = [f'{label}_{story}' for story in stories]
        similar_beams_in_stories = []
        for label_story in similar_label_in_stories:
            similar_beams_in_stories.extend(FreeCAD.ActiveDocument.getObjectsByLabel(label_story))
        for beam in similar_beams_in_stories:
            bases = FreeCAD.ActiveDocument.getObjectsByLabel(f'{beam.Label}_CenterLine')
            if not bases:
                continue
            base = bases[0]
            if has_wall(base):
                continue
            wall = create_wall(base)
            wall.loadpat = loadpat
            wall.weight = mass_per_area
            if height is None:
                next_beam = get_above_beam(beam, all_stories)
                if next_beam is None:
                    if parapet > 0:
                        wall.Height = parapet
                    else:
                        continue
                else:
                    # level_i = beam.InList[0].Elevation
                    # level_j = next_beam.InList[0].Elevation
                    # height = (level_j - level_i)
                    wall.setExpression('Height', f'{next_beam.Name}.Shape.BoundBox.ZMin - {beam.Name}.Shape.BoundBox.ZMax')
            else:
                wall.Height = height
            wall.recompute()
            story_label = beam.Label.split('_')[1]
            story_objects = stories_objects.get(story_label, None)
            if story_objects is None:
                story_objects = [wall]
                stories_objects[story_label] = story_objects
            else:
                story_objects.append(wall)
            if opening_ratio and next_beam:
                win = create_window(wall, opening_ratio)
                story_objects.append(win)
    for story_label, objects in stories_objects.items():
        print(objects)
        story = FreeCAD.ActiveDocument.getObjectsByLabel(story_label)[0]
        current_objects = story.Group.copy()
        story.Group = current_objects + objects

def create_wall(base):
    wall = Arch.makeWall(base)
    if FreeCAD.GuiUp:
        wall.ViewObject.Transparency = 40
        wall.ViewObject.LineWidth = 1
        wall.ViewObject.PointSize = 1
        wall.Base.ViewObject.show()
    wall.addProperty('App::PropertyInteger', 'weight', 'Wall')
    wall.addProperty('App::PropertyString', 'loadpat', 'Wall')
    return wall

def create_window(wall, opening_ratio):
    faces = wall.Shape.Faces
    if not faces:
        return
    areas = [f.Area for f in faces]
    i = areas.index(max(areas))
    pl = WorkingPlane.getPlacementFromFace(wall.Shape.Faces[i])
    percent = math.sqrt(opening_ratio)
    height = percent * wall.Height
    width = percent * wall.Length
    # if width > height and width > 2:
    #     window_type = 'Open 2-pane'
    # elif width < height and height > 2:
    #     window_type = 'Sash 2-pane'
    # else:
    window_type = 'Fixed'
    win = Arch.makeWindowPreset(
            window_type,
            width=width,height=height,h1=100.0,h2=100.0,h3=100.0,w1=200.0,w2=100.0,o1=0.0,o2=100.0,
            placement=pl)
    # win.setExpression('Height', f'{percent} * {wall.Name}.Height')
    # win.setExpression('Width', f'{percent} * {wall.Name}.Length')
    win.recompute()
    v1 = wall.Shape.BoundBox.Center
    v2 = win.Shape.BoundBox.Center
    win.Placement.Base = v1.sub(v2)
    win.Hosts = [wall]
    win.recompute()
    return win

def has_wall(base):
    '''
    check if base has wall in InList
    '''
    inlists = base.InList
    if not inlists:
        return False
    for o in inlists:
        if hasattr(o, 'IfcType') and o.IfcType == 'Wall':
            return True
    return False


if __name__ == '__main__':
    add_wall_on_beams('Dead', 220,
        # stories=('Story1', 'Story9'), 
        opening_ratio=0.3,
        #  height=3000,
        )

