from z3 import *
import pandas as pd

classHourDf = pd.DataFrame(columns=['class', 'day', 'hour', 'course', 'classHourBool'])
classHourDf.set_index(['class', 'day', 'hour', 'course'], inplace=True)
classHourDf.loc[('class2', 0, 1, 'math')] = Bool('math@d0h1@c2')
print(('class2', 0, 1, 'math') in classHourDf.index)
print(classHourDf)
