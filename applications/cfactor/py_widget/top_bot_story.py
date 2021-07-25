import sys
from pathlib import Path

from PyQt5 import uic

cfactor_path = Path(__file__).absolute().parent.parent
civiltools_path = cfactor_path.parent.parent
sys.path.insert(0, civiltools_path)
from etabs_api import functions

story_base, story_window = uic.loadUiType(cfactor_path / 'widgets' / 'top_bot_story.ui')

class StoryForm(story_base, story_window):
    def __init__(self, SapModel, stories, parent=None):
        super(StoryForm, self).__init__()
        self.setupUi(self)
        self.SapModel = SapModel
        self.stories = stories
        self.fill_top_bot_stories()
        self.fill_height_and_no_of_stories()
        self.create_connections()

    def fill_top_bot_stories(self):
        for combo_box in (
            self.bot_x_combo,
            self.top_x_combo,
            # self.bot_y_combo,
            # self.top_y_combo,
        ):
            combo_box.addItems(self.stories)
        n = len(self.stories)
        self.bot_x_combo.setCurrentIndex(0)
        self.top_x_combo.setCurrentIndex(n - 2)
        # self.bot_y_combo.setCurrentIndex(0)
        # self.top_y_combo.setCurrentIndex(n - 2)

    def create_connections(self):
        self.bot_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        self.top_x_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        # self.bot_y_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)
        # self.top_y_combo.currentIndexChanged.connect(self.fill_height_and_no_of_stories)

    def fill_height_and_no_of_stories(self):
        bot_story_x = bot_story_y = self.bot_x_combo.currentText()
        top_story_x = top_story_y = self.top_x_combo.currentText()
        # bot_story_y = self.bot_y_combo.currentText()
        # top_story_y = self.top_y_combo.currentText()
        bot_level_x, top_level_x, bot_level_y, top_level_y = functions.get_top_bot_levels(
                self.SapModel, bot_story_x, top_story_x, bot_story_y, top_story_y, False
                )
        hx, hy = functions.get_heights(self.SapModel, bot_story_x, top_story_x, bot_story_y, top_story_y, False)
        nx, ny = functions.get_no_of_stories(self.SapModel, bot_level_x, top_level_x, bot_level_y, top_level_y)
        self.no_story_x_spinbox.setValue(nx)
        # self.no_story_y_spinbox.setValue(ny)
        self.height_x_spinbox.setValue(hx)
        # self.height_y_spinbox.setValue(hy)

