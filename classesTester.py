from model.Teacher import *
from model.Course import *
from model.Schedule import *
from InteractiveScheduler import InteractiveScheduler

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

intSkej = InteractiveScheduler(skej)
intSkej.start()
