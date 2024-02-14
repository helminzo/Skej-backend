from model.Course import Course

class Class(object):
    def __init__(self, name: str) -> None:
        self.name = name
        self.coursesRequired = []
        self.onAddCourse = None
        self.onRemoveCourse = None
    
    def addCourse(self, course: Course):
        if(self.onAddCourse is not None):
            self.onAddCourse(self, course)
        self.coursesRequired.append(course)
    
    def removeCourse(self, courseName: str) -> bool:
        target = None
        for course in self.coursesRequired:
            if course.courseName == courseName:
                target = course
                break
        if target is None:
            return False
        
        if(self.onRemoveCourse is not None):
            self.onRemoveCourse(target)
        self.coursesRequired.remove(target)
        return True

        