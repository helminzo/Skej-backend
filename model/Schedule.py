from typing import List
from model.Class import Class
from model.Teacher import Teacher
from model.Course import Course

import pandas as pd
from z3 import *

class Schedule():
    # hours is an array of ints, the number of hours in each day of the schedule
    def __init__(self, hours: List[int]) -> None:
        self.hours = hours
        self.totalHours = sum(hours)
        self.classes = []
        self.teachers = []

        # keys order: class, day, hour, course: -> classHourBool
        self.z3_classHourBools = pd.DataFrame(columns=['class', 'course', 'day', 'hour', 'classHourBool'])
        self.z3_classHourBools.set_index(['class', 'course', 'day', 'hour'], inplace=True)

        # keys order: class, day, hour: -> [classHourBool] 
        self.z3_oneClassAtATimeConstraintLists = pd.DataFrame(columns=['class', 'day', 'hour', 'constraints'])
        self.z3_oneClassAtATimeConstraintLists.set_index(['class', 'day', 'hour'], inplace=True)

        # keys order: class, course: -> (hoursRequired, [classHourBool])
        self.z3_hourRequirementConstraints = pd.DataFrame(columns=['class', 'course', 'hoursRequired', 'constraints'])
        self.z3_hourRequirementConstraints.set_index(['class', 'course'], inplace=True)

        # keys order: teacher, day, hour: -> [classHourBool]
        self.z3_teachesOneClassAtATimeConstraintLists = {}

        self.classSchedule = {}
        self.teacherSchedule = {}

    def addClass(self, newClass: Class):
        newClass.onAddCourse = self.onAddCourseToClass
        self.classes.append(newClass)
    
    def addTeacher(self, teacher: Teacher):
        teacher.onAssignCourse = self.onAssignCourseToTeacher
        self.teachers.append(teacher)
    
    def removeClass(self, className: str) -> bool:
        target = None
        for c in self.classes:
            if c.name == className:
                target = c
                break
        if target is None:
            return False
        self.classes.remove(target)
        return True
    
    def onAddCourseToClass(self, _class: Class, course: Course):
        # Add class hour vars
        for i in range(len(self.hours)):
            for j in range(self.hours[i]):
                boolNameStr = f'{course.courseName}@d{i}h{j}@c{_class.name}'
                self.z3_classHourBools.loc[(_class.name, course.courseName, i, j)] = Bool(boolNameStr)
    

    def onAssignCourseToTeacher(self, teacher: Teacher, course: Course):
        for i in range(len(self.hours)):
            for j in range(self.hours[i]):
                for _class in self.classes:
                    if(_class.name in self.z3_classHourBools):
                        if(i in self.z3_classHourBools[_class.name]):
                            if(j in self.z3_classHourBools[_class.name][i]):
                                if(course.courseName in self.z3_classHourBools[_class.name][i][j]):
                                    if(teacher.name not in self.z3_teachesOneClassAtATimeConstraintLists):
                                        self.z3_teachesOneClassAtATimeConstraintLists[teacher.name] = {}
                                    if(i not in self.z3_teachesOneClassAtATimeConstraintLists[teacher.name]):
                                        self.z3_teachesOneClassAtATimeConstraintLists[teacher.name][i] = {}
                                    if(j not in self.z3_teachesOneClassAtATimeConstraintLists[teacher.name][i]):
                                        self.z3_teachesOneClassAtATimeConstraintLists[teacher.name][i][j] = []
            
                                    self.z3_teachesOneClassAtATimeConstraintLists[teacher.name][i][j].append(
                                        self.z3_classHourBools[_class.name][i][j][course.courseName]
                                    )

    def onRemoveCourseFromClass(self, course: Course):
        pass

    def createSchedule(self):
        s = Solver()
        # One class at a time
        for _class in self.z3_oneClassAtATimeConstraintLists:
            for day in self.z3_oneClassAtATimeConstraintLists[_class]:
                for hour in self.z3_oneClassAtATimeConstraintLists[_class][day]:
                    s.add(AtMost(*self.z3_oneClassAtATimeConstraintLists[_class][day][hour], 1))
        
        # Hours requirement
        for _class in self.z3_hourRequirementConstraints:
            for course in self.z3_hourRequirementConstraints[_class]:
                s.add(
                    PbEq(
                        [(x, 1) 
                        for x in self.z3_hourRequirementConstraints[_class][course][1]], 
                        self.z3_hourRequirementConstraints[_class][course][0]
                    )
                )
        
        # Teaches one class at a time
        for teacher in self.z3_teachesOneClassAtATimeConstraintLists:
            for day in self.z3_teachesOneClassAtATimeConstraintLists[teacher]:
                for hour in self.z3_teachesOneClassAtATimeConstraintLists[teacher][day]:
                    s.add(AtMost(*self.z3_teachesOneClassAtATimeConstraintLists[teacher][day][hour], 1))
        
        if(s.check() == sat):
            print("sat")
            model = s.model()
            # Set class schedule
            for _class in self.classes:
                if(_class.name not in self.classSchedule):
                    self.classSchedule[_class.name] = [['Free' for j in range(self.hours[i])] for i in range(len(self.hours))]
                for day in range(len(self.hours)):
                    for hour in range(self.hours[day]):
                        for course in _class.coursesRequired:
                            if(model[self.z3_classHourBools[_class.name][day][hour][course.courseName]]):
                                self.classSchedule[_class.name][day][hour] = course.courseName
            # Set teacher schedule
            for teacher in self.teachers:
                if(teacher.name not in self.teacherSchedule):
                    self.teacherSchedule[teacher.name] = [['Free' for j in range(self.hours[i])] for i in range(len(self.hours))]
                for day in range(len(self.hours)):
                    for hour in range(self.hours[day]):
                        for course in teacher.assignedCourses:
                            for _class in self.classes:
                                if(
                                    course.courseName in self.z3_classHourBools[_class.name][day][hour] and 
                                    model[self.z3_classHourBools[_class.name][day][hour][course.courseName]]
                                ):
                                    self.teacherSchedule[teacher.name][day][hour] = f'{course.courseName}@{_class.name}'
            return True
        return False     
    
    def exportSchedulesToCSV(self, classSchedulePath: str, teacherSchedulePath: str):
        # Open a file for each class
        for _class in self.classSchedule:
            with open(f'{classSchedulePath}/{_class}.csv', 'w') as f:
                for i in range(len(self.hours)):
                    for j in range(self.hours[i]):
                        f.write(f'{self.classSchedule[_class][i][j]},')
                    f.write('\n')
        
        # Open a file for each teacher
        for teacher in self.teacherSchedule:
            with open(f'{teacherSchedulePath}/{teacher}.csv', 'w') as f:
                for i in range(len(self.hours)):
                    for j in range(self.hours[i]):
                        f.write(f'{self.teacherSchedule[teacher][i][j]},')
                    f.write('\n')

