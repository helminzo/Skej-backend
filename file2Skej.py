import csv
from model.Schedule import Schedule
from model.Class import Class
from model.Teacher import Teacher
from model.Course import Course

class file2Skej:
    def __init__(self, days, hours, entityFilename, courseDetailsFileName, classCourseFilename, teacherCourseFilename):
        '''
        days is the number of days in the schedule
        hours is the number of hours per day in the schedule

        Entity file is a CSV file with 3 rows. 
        1) Classes
        2) Teachers
        3) Courses

        courseDetails is a CSV file with 4 columns.
        1) Course Name
        2) Course Hours
        3) Day sparsity ("sparse" or "dense")
        4) Hour sparsity ("sparse" or "dense")

        classCourse is a CSV file with 2 columns.
        1) Class Name
        2) Required course Name

        teacherCourse is a CSV file with 2 columns.
        1) Teacher Name
        2) Assigned course Name
        '''
        self.days = days
        self.hours = hours

        self.entityFilename = entityFilename
        self.courseDetailsFileName = courseDetailsFileName
        self.classCourseFilename = classCourseFilename
        self.teacherCourseFilename = teacherCourseFilename

        # Map class name to class object
        self.classesMap = {}
        # Map teacher name to teacher object
        self.teachersMap = {}
        # Map course name to course object
        self.coursesMap = {}


    def getSkej(self):
        skej = Schedule(hours=[self.hours for i in range(self.days)])
        with open(self.entityFilename) as entityFile:
            entityReader = csv.reader(entityFile)
            classNames = [s.strip() for s in next(entityReader)]
            teacherNames = [s.strip() for s in next(entityReader)]
            courseNames = [s.strip() for s in next(entityReader)]
            print(classNames)
            print(teacherNames)
            print(courseNames)
        for _class in classNames:
            self.classesMap[_class] = Class(_class)
            skej.addClass(self.classesMap[_class])
        print(f"Added {len(classNames)} class(es) to skej")

        for teacher in teacherNames:
            self.teachersMap[teacher] = Teacher(teacher)
            skej.addTeacher(self.teachersMap[teacher])
        print(f"Added {len(teacherNames)} teacher(s) to skej")

        with open(self.courseDetailsFileName) as courseDetailsFile:
            courseDetailsReader = csv.reader(courseDetailsFile)
            for row in courseDetailsReader:
                courseName = row[0].strip()
                courseHours = int(row[1].strip())
                daySparsity = row[2].strip()
                hourSparsity = row[3].strip()
                self.coursesMap[courseName] = Course(courseName=courseName, hoursRequired=courseHours, daySparsity=daySparsity, hourSparsity=hourSparsity)

        numCoursesAdded = 0
        with open(self.classCourseFilename) as classCourseFile:
            classCourseReader = csv.reader(classCourseFile)
            for row in classCourseReader:
                className = row[0].strip()
                courseName = row[1].strip()
                try:
                    self.classesMap[className].addCourse(self.coursesMap[courseName])
                    numCoursesAdded += 1
                except KeyError:
                    print(f"Class {className} not found in classesMap or course {courseName} not found in coursesMap")
                    return
        print(f"Added {numCoursesAdded} courses to classes")

        numCoursesAdded = 0
        with open(self.teacherCourseFilename) as teacherCourseFile:
            teacherCourseReader = csv.reader(teacherCourseFile)
            for row in teacherCourseReader:
                teacherName = row[0].strip()
                courseName = row[1].strip()
                try:
                    self.teachersMap[teacherName].assignCourse(self.coursesMap[courseName])
                    numCoursesAdded += 1
                except KeyError:
                    print(f"Teacher {teacherName} not found in teachersMap or course {courseName} not found in coursesMap")
                    return None
        print(f"Added {numCoursesAdded} courses to teachers")
        
        if(skej.createSchedule()):
            print("Successfully created schedule from files provided")
            return skej
        else:
            print("Schedule not created, problem unsatisfiable")
        return None
            
        

# f2s = file2Skej(2, 2, "ttConfigs/entities.csv", "ttConfigs/courseDetails.csv", "ttConfigs/classCourseMappings.csv", "ttConfigs/teacherCourseMap.csv")
# skej = f2s.getSkej()
# skej.printClassSchedule()
# skej.printTeacherSchedule()