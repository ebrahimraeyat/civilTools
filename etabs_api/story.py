__all__ = ['Story']

class Story:
    def __init__(
                self,
                SapModel=None,
                etabs=None,
                ):
        if not SapModel:
            self.etabs = etabs
            self.SapModel = etabs.SapModel
        else:
            self.SapModel = SapModel

    def get_top_bot_stories(self):
        '''
        return bot_x, top_x, bot_y, top_y stories name"
        '''
        stories = self.SapModel.Story.GetStories()[1]
        bot_story_x = bot_story_y = stories[0]
        top_story_x = top_story_y = stories[-1]
        return bot_story_x, top_story_x, bot_story_y, top_story_y

    def get_top_bot_levels(
                        self,
                        bot_story_x='',
                        top_story_x='',
                        bot_story_y='',
                        top_story_y='',
                        auto_story=True,
                        ):
        self.SapModel.setPresentUnits_2(5, 6, 2)
        if auto_story and not all([bot_story_x, top_story_x, bot_story_y, top_story_y]):
            bot_story_x, top_story_x, bot_story_y, top_story_y = self.get_top_bot_stories()
        bot_level_x = self.SapModel.Story.GetElevation(bot_story_x)[0]    
        top_level_x = self.SapModel.Story.GetElevation(top_story_x)[0]
        bot_level_y = self.SapModel.Story.GetElevation(bot_story_y)[0]    
        top_level_y = self.SapModel.Story.GetElevation(top_story_y)[0]
        return bot_level_x, top_level_x, bot_level_y, top_level_y

    def get_heights(
                    self,
                    bot_story_x='',
                    top_story_x='',
                    bot_story_y='',
                    top_story_y='',
                    auto_story=True,
                    ):
        bot_level_x, top_level_x, bot_level_y, top_level_y = self.get_top_bot_levels(
            bot_story_x, top_story_x, bot_story_y, top_story_y, auto_story)
        hx = top_level_x - bot_level_x
        hy = top_level_y - bot_level_y
        return hx, hy

    def get_no_of_stories(
                        self,
                        bot_level_x = None,
                        top_level_x = None,
                        bot_level_y = None,
                        top_level_y = None,
                        ):
        if not bot_level_x:
            bot_level_x, top_level_x, bot_level_y, top_level_y = self.get_top_bot_levels()
        levels = self.SapModel.Story.GetStories()[2]
        no_of_x_story = len([i for i in levels if bot_level_x < i <= top_level_x])
        no_of_y_story = len([i for i in levels if bot_level_y < i <= top_level_y])
        return no_of_x_story, no_of_y_story

    def get_story_names(self):
        return self.SapModel.Story.GetNameList()[1]