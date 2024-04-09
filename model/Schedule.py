from model.Class import Class
from model.Teacher import Teacher
from model.Course import Course

import os
import pandas as pd
from z3 import *
from typing import List
from tabulate import tabulate
import copy

class Schedule():
    # hours is an array of ints, the number of hours in each day of the schedule
    def __init__(self, hours: List[int]) -> None:
        self.hours = hours
        self.totalHours = sum(hours)
        self.classes = []
        self.teachers = []

        # keys order: class, course, day, hour: -> classHourBool
        self.z3_classHourBools = pd.DataFrame(columns=['class', 'course', 'day', 'hour', 'classHourBool'])
        self.z3_classHourBools.set_index(['class', 'course', 'day', 'hour'], inplace=True)

        # keys order: teacher, day, hour: -> classHourBool
        self.z3_teachesOneClassAtATimeConstraintLists = pd.DataFrame(columns=['teacher', 'day', 'hour', 'constrainedClassHourName', 'classHourBool'])
        self.z3_teachesOneClassAtATimeConstraintLists.set_index(['teacher', 'day', 'hour', 'constrainedClassHourName'], inplace=True) 
        
        self.tweaks = []

        self.classSchedule = {}
        self.teacherSchedule = {}

        self.solver = Optimize()

    def addClass(self, newClass: Class):
        newClass.onAddCourse = self.onAddCourseToClass
        for course in newClass.coursesRequired:
            self.onAddCourseToClass(newClass, course)
        self.classes.append(newClass)

    def addTeacher(self, teacher: Teacher):
        teacher.onAssignCourse = self.onAssignCourseToTeacher
        for course in teacher.assignedCourses:
            self.onAssignCourseToTeacher(teacher, course)
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
                boolNameStr = f'{course.name}@d{i}h{j}@{_class.name}'
                self.z3_classHourBools.loc[(_class.name, course.name, i, j)] = Bool(boolNameStr)


    def onAssignCourseToTeacher(self, teacher: Teacher, course: Course):
        for i in range(len(self.hours)):
            for j in range(self.hours[i]):
                for _class in self.classes:
                    if(course in _class.coursesRequired):
                        # Get class hour bool
                        classHourBool = self.z3_classHourBools.loc[(_class.name, course.name, i, j), 'classHourBool']
                        # Add to teachesOneClassAtATimeConstraintLists
                        self.z3_teachesOneClassAtATimeConstraintLists.loc[(teacher.name, i, j, f'{course.name}@d{i}h{j}@{_class.name}')] = classHourBool


    def onRemoveCourseFromClass(self, course: Course):
        pass

    def createConstraints(self):
        # HARD CONSTRAINTS
        # One class at a time
        for _class in self.classes:
            for day in range(len(self.hours)):
                for hour in range(self.hours[day]):
                    self.solver.add(
                        AtMost(*self.z3_classHourBools.loc[_class.name, :, day, hour]['classHourBool'].to_list(), 1)
                    ) 

        # Hours requirement
        for _class in self.classes:
            for course in _class.coursesRequired:
                self.solver.add(
                    PbEq(
                        [(x, 1)
                        for x in self.z3_classHourBools.loc[_class.name, course.name, :, :]['classHourBool'].to_list()],
                        course.hoursRequired
                    )
                )

        # Teaches one class at a time
        for teacher in self.teachers:
            for day in range(len(self.hours)):
                for hour in range(self.hours[day]):
                    constraintList =self.z3_teachesOneClassAtATimeConstraintLists.loc[teacher.name, day, hour]['classHourBool'].to_list()
                    if len(constraintList) > 0:
                        self.solver.add(
                            AtMost(
                                *constraintList,
                                1
                            )
                        )

        # SOFT CONSTRAINTS
        # Sparsity requirements
        # Spread score : Spread across days
        for _class in self.classes:
            for course in _class.coursesRequired:
                spread_score = 0
                # If at least one hour is taken a day, add 1 to spread_score
                for day in range(len(self.hours)):
                    spread_score += If(
                        Or(
                            *self.z3_classHourBools.loc[_class.name, course.name, day, :]['classHourBool'].to_list()
                        ),
                        course.daySparsityWeight,
                        0
                    )
                if(course.daySparsity == "sparse"):
                    self.solver.maximize(spread_score)
                elif(course.daySparsity == "dense"):
                    self.solver.minimize(spread_score)

        # Spread score : Spread across hours
        for _class in self.classes:
            for course in _class.coursesRequired:
                spread_score = 0
                for day in range(len(self.hours)):
                    # If two consecutive hours are taken, add 1 to spread_score
                   for hour in range(self.hours[day] - 1):
                          spread_score += If(
                            And(
                                 self.z3_classHourBools.loc[_class.name, course.name, day, hour]['classHourBool'],
                                 self.z3_classHourBools.loc[_class.name, course.name, day, hour + 1]['classHourBool']
                            ),
                            course.hourSparsityWeight,
                            0
                          )
                if(course.hourSparsity == "sparse"):
                    self.solver.minimize(spread_score)
                elif(course.hourSparsity == "dense"):
                    self.solver.maximize(spread_score)  



    def createSchedule(self, createConstraints: bool = True):
        if createConstraints:
            self.createConstraints()
        if(self.solver.check() == sat):
            print("Schedule created!")
            model = self.solver.model()
            # Set class schedule
            for _class in self.classes:
                if(_class.name not in self.classSchedule):
                    self.classSchedule[_class.name] = [['Free' for j in range(self.hours[i])] for i in range(len(self.hours))]
                for day in range(len(self.hours)):
                    for hour in range(self.hours[day]):
                        for course in _class.coursesRequired:
                            if(model[self.z3_classHourBools.loc[_class.name, course.name, day, hour]['classHourBool']]):
                                self.classSchedule[_class.name][day][hour] = course.name
            # Set teacher schedule
            for teacher in self.teachers:
                if(teacher.name not in self.teacherSchedule):
                    self.teacherSchedule[teacher.name] = [['Free' for j in range(self.hours[i])] for i in range(len(self.hours))]
                for day in range(len(self.hours)):
                    for hour in range(self.hours[day]):
                        for course in teacher.assignedCourses:
                            classesToCheck = [c for c in self.classes if course in c.coursesRequired]
                            for _class in classesToCheck:
                                if(
                                    model[self.z3_classHourBools.loc[_class.name, course.name, day, hour]['classHourBool']]
                                ):
                                    self.teacherSchedule[teacher.name][day][hour] = f'{course.name}@{_class.name}'
            return True
        return False
    
    def printTeacherSchedule(self):
        print("\n-----------------\nTeacher Schedule\n-----------------\n")
        for teacher in self.teacherSchedule:
            print(f"Teacher: {teacher}")
            print(tabulate(self.teacherSchedule[teacher], headers=[i for i in range(self.hours[0])], tablefmt='grid', showindex='always'))
            print("\n")
    
    def printClassSchedule(self):
        print("\n-----------------\nClass Schedule\n-----------------\n")
        for _class in self.classSchedule:
            print(f"Class: {_class}")
            print(tabulate(self.classSchedule[_class], headers=[i for i in range(self.hours[0])], tablefmt='grid', showindex='always'))
            print("\n")  

    def exportSchedulesToCSV(self, classScheduleFolderPath: str, teacherScheduleFolderPath: str):
        # Create folders if they don't exist
        if not os.path.exists(classScheduleFolderPath):
            os.makedirs(classScheduleFolderPath)
        if not os.path.exists(teacherScheduleFolderPath):
            os.makedirs(teacherScheduleFolderPath)
        # Open a file for each class
        for _class in self.classSchedule:
            with open(f'{classScheduleFolderPath}/{_class}.csv', 'w') as f:
                for i in range(len(self.hours)):
                    for j in range(self.hours[i]):
                        f.write(f'{self.classSchedule[_class][i][j]},')
                    f.write('\n')

        # Open a file for each teacher
        for teacher in self.teacherSchedule:
            with open(f'{teacherScheduleFolderPath}/{teacher}.csv', 'w') as f:
                for i in range(len(self.hours)):
                    for j in range(self.hours[i]):
                        f.write(f'{self.teacherSchedule[teacher][i][j]},')
                    f.write('\n')
     # Tweaking API
    def setClassHour(self, className: str, courseName: str, day: int, hour: int, value=True, printDiffs=False, shouldTweak=True):
        if(day >= len(self.hours) or day < 0):
            print("ERROR: Invalid day")
            return False
        if(hour >= self.hours[day] or hour < 0):
            print("ERROR: Invalid hour")
            return False
        self.solver.push()
        self.solver.add(self.z3_classHourBools.loc[(className, courseName, day, hour), 'classHourBool'] == value)
        if(self.solver.check() == sat):
            if(shouldTweak):
                self.tweaks.append(
                    {
                        "action": "set",
                        "className": className,
                        "courseName": courseName,
                        "day": day,
                        "hour": hour,
                        "value": value
                    }
                )
            if printDiffs:
                oldClassSchedule = copy.deepcopy(self.classSchedule)
                oldTeacherSchedule = copy.deepcopy(self.teacherSchedule.copy())
                self.createSchedule(createConstraints=False)
                print("\nChanges in class schedule")
                for _class in self.classSchedule:
                    for i in range(len(self.hours)):
                        for j in range(self.hours[i]):
                            if oldClassSchedule[_class][i][j] != self.classSchedule[_class][i][j]:
                                print(f'{_class} @ day {i} hour {j} : {oldClassSchedule[_class][i][j]} -> {self.classSchedule[_class][i][j]}')
                print()
                print("\nChanges in teacher schedule")
                for teacher in self.teacherSchedule:
                    for i in range(len(self.hours)):
                        for j in range(self.hours[i]):
                            if oldTeacherSchedule[teacher][i][j] != self.teacherSchedule[teacher][i][j]:
                                print(f'{teacher} @ day {i} hour {j} : {oldTeacherSchedule[teacher][i][j]} -> {self.teacherSchedule[teacher][i][j]}')
            else:
                self.createSchedule(createConstraints=False)
            return True
        self.solver.pop()
        print("Schedule unsatisfiable")
        return False
    
    def swapHoursForClass(self, className: str, day1: int, hour1: int, day2: int, hour2: int):
        if(self.classSchedule == {}):
            print("ERROR: Schedule not created yet")
            return False
        if(day1 >= len(self.hours) or day2 >= len(self.hours) or day1 < 0 or day2 < 0):
            print("ERROR: Invalid day")
            return False
        if(hour1 >= self.hours[day1] or hour2 >= self.hours[day2] or hour1 < 0 or hour2 < 0):
            print("ERROR: Invalid hour")
            return False
        course1 = self.classSchedule[className][day1][hour1]
        course2 = self.classSchedule[className][day2][hour2]
        if course2 != 'Free':
            self.solver.add(self.z3_classHourBools.loc[(className, course2, day1, hour1), 'classHourBool'] == True)
        if course1 != 'Free':
            self.solver.add(self.z3_classHourBools.loc[(className, course1, day2, hour2), 'classHourBool'] == True)
        
    def removeTweak(self, index: int):
        if index >= len(self.tweaks):
            print("Index out of range")
            return
        tweak = self.tweaks[index]
        totalTweaks = len(self.tweaks)
        for i in range(totalTweaks - index):
            self.solver.pop()
        # push all tweaks after index back
        for i in range(index + 1, totalTweaks):
            tweak = self.tweaks[i]
            if tweak['action'] == 'set':
                self.setClassHour(tweak['className'], tweak['courseName'], tweak['day'], tweak['hour'], tweak['value'], shouldTweak=False)
            elif tweak['action'] == 'swap':
                self.swapHoursForClass(tweak['className'], tweak['day1'], tweak['hour1'], tweak['day2'], tweak['hour2'])
        self.tweaks.pop(index)
    