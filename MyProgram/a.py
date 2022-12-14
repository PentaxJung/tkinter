from pandas import read_csv, pivot_table, melt
from time import process_time
import timeit

def run():
    in_file = '../1250auto.in'
    pop_file = '../pop.in'

    whole_seg_time = process_time()

    read_data_time = process_time()
    data = read_csv(in_file, skiprows=2, header=None, names=['O', 'D', 'Traffic'])
    data_pop = read_csv(pop_file, skiprows=1, header=None, names=['before', 'after', 'ratio'])
    print(" 데이터 불러오기 소요시간: " + str(process_time() - read_data_time))

    # O/D 매트릭스 생성(self.data_OD)
    const_OD_time = process_time()
    data_OD = pivot_table(data, values='Traffic', index='O', columns='D')
    print(data_OD)
    print(" - OD 구축 소요시간: " + str(process_time() - const_OD_time))

    pop_process_time = process_time()
    seg_zone_df = data_pop[data_pop.duplicated(subset='before', keep=False)].groupby('before')
    seg_data = [seg_zone_df.get_group(name) for name, group in seg_zone_df]
    a = [dict(before=int(item.values[0][0]),
              after=[int(item['after'].iloc[i]) for i in range(len(item))],
              ratio=[item['ratio'].iloc[i] for i in range(len(item))]) for item in seg_data]

    target_zone = [a[i]['before'] for i in range(len(a))]
    seg_zone = [a[i]['after'] for i in range(len(a))]
    pop_ratio = [a[i]['ratio'] for i in range(len(a))]
    print(" - pop 참조 소요시간: " + str(process_time() - pop_process_time))

    start_time = process_time()
    data_judge_be = data_OD.copy(deep=False)
    data_judge_be.loc['Total'] = data_judge_be.sum(axis=0)  # Total sum per column:
    data_judge_be.loc[:, 'Total'] = data_judge_be.sum(axis=1)  # Total sum per row:

    for target_zone_num, seg_zone_list, pop_list in zip(target_zone, seg_zone, pop_ratio):
        for index, seg_zone_num in enumerate(seg_zone_list):
            data_OD.loc[seg_zone_num] = data_OD.loc[target_zone_num] * pop_list[index]
            data_OD.loc[:, seg_zone_num] = data_OD.loc[:, target_zone_num] * pop_list[index]
    print(" - 세분화 작업 소요시간: " + str(process_time() - start_time))

    delete_time = process_time()
    for i in target_zone:
        data_OD.loc[i] = 0
        data_OD.loc[:, i] = 0
    data_OD = data_OD.astype('float64').round(2)
    print(" - 기존 존 삭제 소요시간: " + str(process_time() - delete_time))

    # 세분화 후 Total 판별용 매트릭스 생성(data_judge_af)
    judge_time = process_time()
    data_judge_af = data_OD.copy(deep=False)
    data_judge_af.loc['Total', :] = data_judge_af.sum(axis=0)
    data_judge_af.loc[:, 'Total'] = data_judge_af.sum(axis=1)
    judge = abs(data_judge_be['Total']['Total'] / data_judge_af['Total']['Total'])
    if 0.9999 < judge < 1.0001:
        print("Zone segmentation is successfully done!")
    else:
        print("Error...")
        print(" 오류 . . .")
        print(str(judge))
    print(" - 판별 작업 소요시간: " + str(process_time() - judge_time))

    write_time = process_time()
    # file = open('../wow.txt', 'w', encoding='utf8')
    # header = 't matrices\na matrix=mf01 2016auto\n'
    # file.write(header)
    # for i in data_OD.index:
    #     for j in data_OD.columns:
    #         lines = '%d\t%d\t%f\n' % (i, j, data_OD.at[i, j])
    #         file.write(lines)
    data_write = data_OD.T.unstack()
    print(data_write)
    data_write.to_csv('../wow.txt', sep=',', na_rep=0)
    print(" - 파일 쓰기 소요시간: " + str(process_time() - write_time))

    print(" - 전체 세분화 소요시간: " + str(process_time() - whole_seg_time))

print(timeit.timeit(run, number=1))