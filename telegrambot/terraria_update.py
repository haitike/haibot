import datetime

class TerrariaUpdate(object):
    def __init__(self, user="Anon"):
        self.user = user
        self.date = datetime.datetime.now().replace(microsecond=0)
        self.is_milestone = False

    def toDBCollection(self):
        return vars(self)

class TerrariaStatusUpdate(TerrariaUpdate):
    def __init__(self, user="Anon", status=False, ip=None):
        super(TerrariaStatusUpdate, self).__init__(user)
        self.status = status
        self.ip = ip

class TerrariaMilestoneUpdate(TerrariaUpdate):
    def __init__(self, user="Anon", text="Milestone"):
        super(TerrariaMilestoneUpdate, self).__init__(user)
        self.milestone_text = text
        self.is_milestone = True