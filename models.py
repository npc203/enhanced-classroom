class Course:
    def __init__(self, id, **kwargs) -> None:
        self.id = kwargs["id"]
        self.hidden = kwargs["hidden"]
        self.last_scrape = kwargs["last_scrape"]
        self.name = kwargs["name"]
        self.section = kwargs["section"]
        self.descriptionHeading = kwargs["descriptionHeading"]
        self.room = kwargs["room"]
        self.ownerId = kwargs["ownerId"]
        self.creationTime = kwargs["creationTime"]
        self.updateTime = kwargs["updateTime"]
        self.courseState = kwargs["courseState"]
        self.alternateLink = kwargs["alternateLink"]
        self.teacherGroupEmail = kwargs["teacherGroupEmail"]
        self.courseGroupEmail = kwargs["courseGroupEmail"]
        self.guardiansEnabled = kwargs["guardiansEnabled"]
        self.calendarId = kwargs["calendarId"]


class Topic:
    def __init__(self, topicId, **kwargs):
        self.courseId = kwargs["courseId"]
        self.topicId = kwargs["topicId"]
        self.name = kwargs["name"]
        self.updateTime = kwargs["updateTime"]
