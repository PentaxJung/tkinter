from pandas import DataFrame, read_csv, pivot_table

data = read_csv('./2014auto.in', skiprows=2, header=None, names=['O', 'D', 'Traffic'])
data_OD = pivot_table(data, values='Traffic', index='O', columns='D')
target_zone = [1, 3, 50, 70]
for i in target_zone:
    print('target zone:', i)
    # data_OD.loc[i] = 0
    # data_OD.loc[:, i] = 0
    data_OD = data_OD.drop([i], axis=0).drop([i], axis=1)
    print(data_OD)