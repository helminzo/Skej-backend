from model.Teacher import *
from model.Course import *
from model.Schedule import *
import pprint

skej = Schedule(hours = [6,6,6,6,6])
cs4y = Class("CS-4")
cs3y = Class("CS-3")
cs2y = Class("CS-2")

skej.addClass(cs4y)
skej.addClass(cs3y)
skej.addClass(cs2y)

# 4th year courses
dc = Course("CST402: DC", 3)
pe3 = Course("PE3", 3)
pe4 = Course("PE4", 3)
pe5 = Course("PE5", 3)
p2 = Course("Project Phase-2", 18)

# 3rd year courses
cd = Course("CST302: CD", 4)
cgip = Course("CST304: CGIP", 4)
aad = Course("CST306: AAD", 4)
ccw = Course("CST308: CCW", 4)
elec = Course("PE1", 3)
miniproj = Course("CSD334: Miniproject", 3)
netLab = Course("CSL332: Network Lab", 3)

# 2nd year courses
coa = Course("CST202: CoA", 4)
dbms = Course("CST204: DBMS", 4)
osCourse = Course("CST206: OS", 4)
digitalLab = Course("CSL202: Digital Lab", 3)
osLab = Course("CSL204: OS Lab", 3)
constitution = Course("MCN202: CI", 2)
ethics = Course("HUT200: PE", 2)




cs4y.addCourse(dc)
cs4y.addCourse(pe3)
cs4y.addCourse(pe4)
cs4y.addCourse(pe5)
cs4y.addCourse(p2)

cs3y.addCourse(cd)
cs3y.addCourse(cgip)
cs3y.addCourse(aad)
cs3y.addCourse(ccw)
cs3y.addCourse(miniproj)
cs3y.addCourse(netLab)
cs3y.addCourse(elec)

cs2y.addCourse(coa)
cs2y.addCourse(dbms)
cs2y.addCourse(osCourse)
cs2y.addCourse(digitalLab)
cs2y.addCourse(osLab)
cs2y.addCourse(constitution)
cs2y.addCourse(ethics)

helen = Teacher("Prof. Helen KJ")
ajayJames = Teacher("Dr. Ajay James")
princyAnn = Teacher("Ms. Princy Ann Thomas")
rahmathullah = Teacher("Mr. Rahmathullah K")
dileeshED = Teacher("Dr. Dileesh ED")
bisnaND = Teacher("Ms. Bisna ND")
ezudheenP = Teacher("Dr. Ezudheen P")
geomat = Teacher("Mr. George Mathew")
soniP = Teacher("Mr. Soni P")
panchamiVU = Teacher("Ms. Panchami VU")
umasreeAK = Teacher("Ms. Umasree AK")
remyaK = Teacher("Ms. Remya K")
shehinShams = Teacher("Mr. Shehin Shams")
sakshiJ = Teacher("Ms. Sakshi Jain")
subinaT = Teacher("Ms. Subina T")
rinjuOR = Teacher("Ms. Rinju OR")
Roshni = Teacher("Ms. Roshni")

skej.addTeacher(helen)
skej.addTeacher(ajayJames)
skej.addTeacher(princyAnn)
skej.addTeacher(rahmathullah)
skej.addTeacher(dileeshED)
skej.addTeacher(bisnaND)
skej.addTeacher(ezudheenP)
skej.addTeacher(geomat)
skej.addTeacher(soniP)
skej.addTeacher(panchamiVU)
skej.addTeacher(umasreeAK)
skej.addTeacher(remyaK)
skej.addTeacher(shehinShams)
skej.addTeacher(sakshiJ)
skej.addTeacher(subinaT)
skej.addTeacher(rinjuOR)
skej.addTeacher(Roshni)

helen.assignCourse(miniproj)

ajayJames.assignCourse(dbms)

princyAnn.assignCourse(p2)

rahmathullah.assignCourse(netLab)

dileeshED.assignCourse(coa)
dileeshED.assignCourse(digitalLab)

bisnaND.assignCourse(osCourse)

ezudheenP.assignCourse(miniproj)
ezudheenP.assignCourse(elec)

geomat.assignCourse(p2)
geomat.assignCourse(pe3)

# soniP.assignCourse(p2)
soniP.assignCourse(miniproj)
soniP.assignCourse(ccw)

panchamiVU.assignCourse(pe3)
panchamiVU.assignCourse(constitution)
panchamiVU.assignCourse(osLab)

umasreeAK.assignCourse(cgip)
umasreeAK.assignCourse(pe5)
umasreeAK.assignCourse(osLab)

remyaK.assignCourse(dc)
remyaK.assignCourse(netLab)

shehinShams.assignCourse(cd)
shehinShams.assignCourse(ethics)
shehinShams.assignCourse(digitalLab)

sakshiJ.assignCourse(pe4)
sakshiJ.assignCourse(osLab)

subinaT.assignCourse(aad)
subinaT.assignCourse(pe5)
subinaT.assignCourse(digitalLab)

rinjuOR.assignCourse(pe3)
Roshni.assignCourse(pe4)
Roshni.assignCourse(netLab)

skej.createSchedule()
pprint.pprint(skej.classSchedule)
pprint.pprint(skej.teacherSchedule)

skej.exportSchedulesToCSV("ClassSchedules", "TeacherSchedules")
