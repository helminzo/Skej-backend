# This file is the main file for the Interactive Scheduler application
from model.Schedule import Schedule
import tabulate
import readline
import json
from file2Skej import file2Skej

# Enable tab completion
readline.parse_and_bind('tab: complete')
class InteractiveScheduler:
    def __init__(self, schedule=None):
        if schedule is not None:
            self.schedule = schedule
        else:
            self.schedule = Schedule()
        self.cmd = ""

    def fileInit(self, config=None):
        days = int(input("Enter the number of days in the schedule: "))
        hours = int(input("Enter the number of hours per day in the schedule: "))
        entityFilename = None
        courseDetailsFileName = None
        classCourseFilename = None
        teacherCourseFilename = None

        if config is not None:
            with open(config) as configFile:
                config = json.load(configFile)
                entityFilename = config["entityFilename"]
                courseDetailsFileName = config["courseDetailsFilename"]
                classCourseFilename = config["classCourseFilename"]
                teacherCourseFilename = config["teacherCourseFilename"]
        else:
            while entityFilename is None:
                try:
                    entityFilename = input("Enter the entity filename: ")
                    with open(entityFilename) as entityFile:
                        pass
                except FileNotFoundError:
                    print("File not found. Please enter a valid filename.")
                    entityFilename = None
            while courseDetailsFileName is None:
                try:
                    courseDetailsFileName = input("Enter the course details filename: ")
                    with open(courseDetailsFileName) as courseDetailsFile:
                        pass
                except FileNotFoundError:
                    print("File not found. Please enter a valid filename.")
                    courseDetailsFileName = None
            
            while classCourseFilename is None:
                try:
                    classCourseFilename = input("Enter the class<->course map filename: ")
                    with open(classCourseFilename) as classCourseFile:
                        pass
                except FileNotFoundError:
                    print("File not found. Please enter a valid filename.")
                    classCourseFilename = None
            
            while teacherCourseFilename is None:
                try:
                    teacherCourseFilename = input("Enter the teacher<->course map filename: ")
                    with open(teacherCourseFilename) as teacherCourseFile:
                        pass
                except FileNotFoundError:
                    print("File not found. Please enter a valid filename.")
                    teacherCourseFilename = None

        f2s = file2Skej(
            days=days, hours=hours,
            entityFilename=entityFilename,
            courseDetailsFileName=courseDetailsFileName,
            classCourseFilename=classCourseFilename,
            teacherCourseFilename=teacherCourseFilename
        )
        self.schedule = f2s.getSkej()

    def parse(self, cmd):
        words = cmd.split(" ")
        if words[0] == "file-init":
            if len(words) > 2:
                print("Usage: file-init [config_file_path]")
                return
            if len(words) == 1:
                self.fileInit()
            else:
                # Check if the file exists
                try:
                    with open(words[1]) as f:
                        pass
                except FileNotFoundError:
                    print(f"Config file {words[1]} not found. Please enter a valid filename.")
                    return
                self.fileInit(config=words[1])

        if words[0] == "print":
            if len(words) == 1:
                print("Usage: print <type_of_schedule> (either 'teacher' or 'class')")
                return
            if words[1] == "teacher":
                self.schedule.printTeacherSchedule()
            elif words[1] == "class":
                self.schedule.printClassSchedule()

        elif words[0] == "set":
            if len(words) < 5:
                print("Usage: set <class> <day> <hour> <course> \nOptions: --show-diff: Shows the differences between the previous and current schedule")
                return
            self.schedule.setClassHour(className=words[1], day=int(words[2]), hour=int(words[3]), courseName=words[4], printDiffs=(len(words) == 6 and words[5] == "--show-diff"))
       
        elif words[0] == "export":
            if len(words) == 1:
                print("Usage: export <teacher_sched_folder_path> <class_sched_folder_path>")
                return
            self.schedule.exportSchedulesToCSV(words[1], words[2])
        
        elif words[0] == "tweaks":
            if len(words) == 1:
                print("Usage: tweaks <cmd> args")
                return
            if words[1] == "show":
                print(tabulate.tabulate(self.schedule.tweaks, showindex="always", headers="keys", tablefmt="psql"))
            if words[1] == "rm":
                if len(words) < 3:
                    print("Usage: tweaks rm <index>")
                    return
                index = int(words[2])
                if index >= len(self.schedule.tweaks):
                    print("Index out of range")
                    return
                self.schedule.removeTweak(index)
            
    def start(self):
        while(self.cmd != "exit"):
            self.cmd = input("\nskej$ ")
            self.parse(self.cmd)