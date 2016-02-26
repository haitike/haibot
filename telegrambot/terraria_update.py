from datetime import datetime
from bson.objectid import ObjectId
# TODO i18n multiple files

def build_from_DB_document(document):
    """ Method used to build Project objects from JSON data returned from MongoDB """
    if document is not None:
        try:
            if not document["is_milestone"]:
               return Status(
                    document['user'],
                    document['status'],
                    document['ip'],
                    document['date'],
                    project_id=document.get('_id', None))
            else:
                return Milestone(
                    document['user'],
                    document['milestone_text'],
                    document['date'],
                    project_id=document.get('_id', None))
        except KeyError as e:
            raise Exception("Key not found in json_data: %s" % (repr(e)))
    else:
        raise Exception("No data to create Project from!")

class Status(object):
    def __init__(self, user, status, ip, date=datetime.utcnow(), project_id=None):
        if project_id is None:
            self._id = ObjectId()
        else:
            self._id = project_id
        self.user = user
        self.status = status
        self.ip = ip
        self.date = date
        self.is_milestone = False

    def get_text(self, with_date=False):
        text= ""

        if with_date:
            fdate = self.date.strftime("%d/%m/%y %H:%M")
            text+= "[%s] " % fdate
        if self.status:
            text+= _("(%s) Terraria server is On (IP:%s)") % (self.user , self.ip)
        else:
            text+= _("(%s) Terraria server is Off")  % (self.user)

        return text

    def toDBCollection(self):
        return self.__dict__  #Equivalent to vars(object)

class Milestone(object):
    def __init__(self, user, text, date=datetime.utcnow(), project_id=None ):
        if project_id is None:
            self._id = ObjectId()
        else:
            self._id = project_id
        self.user = user
        self.milestone_text = text
        self.date = date
        self.is_milestone = True

    def get_text(self, with_date=False):
        if with_date:
            fdate = self.date.strftime("%d/%m/%y %H:%M")
            return _("[%s] (%s) Milestone: %s") % (fdate, self.user , self.milestone_text)
        else:
            return _("(%s) Milestone: %s") % (self.user , self.milestone_text)

    def toDBCollection(self):
        return self.__dict__  #Equivalent to vars(object)