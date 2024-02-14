from z3 import *
from model.Teacher import Teacher
classes = ['1', '2']
courses = ['CST191', 'CST103', 'CST105', 'CST201', 'CST203', 'CST205']
# Create an enumsort from courses

Course, courseVars = EnumSort('Course', courses)
Class, classVars = EnumSort('Class', classes)
firstHourFunction = Function('f', Class, Course)
s = Solver()
clauseOne = Or(
    firstHourFunction(classVars[0]) == courseVars[0],
    firstHourFunction(classVars[0]) == courseVars[1],
    firstHourFunction(classVars[0]) == courseVars[2]
)
clauseTwo = Or(
    firstHourFunction(classVars[1]) == courseVars[3],
    firstHourFunction(classVars[1]) == courseVars[4],
    firstHourFunction(classVars[1]) == courseVars[5]
)
s.add(clauseOne, clauseTwo)
print(s.check())
print(s.model())
