from model.Teacher import *
from model.Course import *
from model.Schedule import *
import pprint


skej = Schedule(hours = [2,2])
cs4y = Class("4A")
cs3y = Class("3A")
t1 = Teacher("Dileesh E.D")
t2 = Teacher("Ezudheen P.")
c1 = Course("CST401", 2)
c2 = Course("CST403", 1)
c3 = Course("CST405", 1)

e1 = Course("CST301", 2)
e2 = Course("CST303", 1)
e3 = Course("CST305", 1)

skej.addClass(cs4y)
cs4y.addCourse(c1)
cs4y.addCourse(c2)
cs4y.addCourse(c3)
skej.addClass(cs3y)
cs3y.addCourse(e1)
cs3y.addCourse(e2)
cs3y.addCourse(e3)

skej.addTeacher(t1)
t1.assignCourse(c1)
t1.assignCourse(e2)
t1.assignCourse(e3)
skej.addTeacher(t2)
t2.assignCourse(c2)
t2.assignCourse(c3)
t2.assignCourse(e1)

print("Class hour bools")
pprint.pprint(skej.z3_classHourBools, indent=4)
print("One class at at time constraint lists")
pprint.pprint(skej.z3_oneClassAtATimeConstraintLists, indent=4)
print("Hour requirement constraints")
pprint.pprint(skej.z3_hourRequirementConstraints, indent=4)
print("Teaches one class at a time constraints")
pprint.pprint(skej.z3_teachesOneClassAtATimeConstraintLists, indent=4)

skej.createSchedule()
pprint.pprint(skej.classSchedule, indent=4)
pprint.pprint(skej.teacherSchedule, indent=4)