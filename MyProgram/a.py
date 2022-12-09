from pandas import read_csv, DataFrame
from numpy import divide
import timeit

def run():
    in_file = '../2016auto.in'
    pop_file = '../pop.in'

    data = read_csv(in_file, skiprows=2, header=None, names=['O', 'D', 'Traffic'])
    data_pop = read_csv(pop_file, skiprows=1, header=None, names=['before', 'after', 'ratio'])

    # O/D 매트릭스 생성(self.data_2)
    col = [int(i) for i in data['D'].unique()]
    row = [int(i) for i in data['O'].unique()]


    data_OD = DataFrame(columns=col, index=row)
    n = 0
    for i in col:
        for j in row:
            data_OD.at[i, j] = data['Traffic'][n]
            n = n + 1
    seg_zone_df = data_pop[data_pop.duplicated(subset='before', keep=False)].groupby('before')
    seg_data = (seg_zone_df.get_group(name) for name, group in seg_zone_df)
    a = [dict(before=int(item.values[0][0]),
              after=[int(item['after'].iloc[i]) for i in range(len(item))],
              ratio=[item['ratio'].iloc[i] for i in range(len(item))]) for item in seg_data]
    print(a)
    target_zone = [a[i]['before'] for i in range(len(a))]
    seg_zone = [a[i]['after'] for i in range(len(a))]
    pop_ratio = [a[i]['ratio'] for i in range(len(a))]

    # Total 판별용 매트릭스 생성(data_judge_be / deep copy X)
    data_judge_be = data_OD.copy(deep=False)
    data_judge_be.loc['Total', :] = data_judge_be.sum(axis=0) # Total sum per column:
    data_judge_be.loc[:, 'Total'] = data_judge_be.sum(axis=1) # Total sum per row:

    for i in range(len(target_zone)):
        for n in range(len(seg_zone[i])):
            data_OD.loc[seg_zone[i][n]] = data_OD.loc[target_zone[i]] * pop_ratio[i][n]
            data_OD.loc[:, seg_zone[i][n]] = data_OD.loc[:, target_zone[i]] * pop_ratio[i][n]

    for i in range(len(target_zone)):
        data_OD.loc[target_zone[i]] = 0
        data_OD.loc[:, target_zone[i]] = 0
    data_OD = data_OD.astype('float64').round(2)

    # 세분화 후 Total 판별용 매트릭스 생성(data_judge_af)
    data_judge_af = data_OD.copy(deep=False)
    data_judge_af.loc['Total', :] = data_judge_af.sum(axis=0)
    data_judge_af.loc[:, 'Total'] = data_judge_af.sum(axis=1)
    judge = abs(data_judge_be['Total']['Total'] / data_judge_af['Total']['Total'])
    if 0.9999 < judge < 1.0001:
        print("\nZone segmentation is successfully done!")
print(timeit.timeit(run, number=1))