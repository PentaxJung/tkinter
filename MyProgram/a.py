import pandas as pd
import numpy as np

df = pd.DataFrame([(0.211, .352*1/6), (.061, .677),
                   (.686, .033), (.621, .178)])
print(df)
for i in range(2):
    for j in range(4):
        print(type(df[i][j]))

df = df.round(2)
print(df)