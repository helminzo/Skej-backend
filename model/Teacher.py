from typing import List
from model.Course import *
from model.Class import *

class Teacher():
    def __init__(self, name, assignedCourses=None, coursesCanTeach=None, maxHoursInSchedule=40):
        self.name = name
        self.assignedCourses = assignedCourses or []
        self.coursesCanTeach = coursesCanTeach or []
        self.maxHoursInSchedule = maxHoursInSchedule
        self.onAssignCourse = None
    
    def assignCourse(self, course: Course):
        if self.onAssignCourse is not None:
            self.onAssignCourse(self, course)
        self.assignedCourses.append(course)
    
    def assignCourses(self, courses: List[Course]):
        self.assignedCourses += courses