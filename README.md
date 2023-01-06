[index.py]
1. file_system 연결(완)
 - file_system 모듈화와 연결 작업

2. 통합 UI 구축 중
 - file_system 연결(완)
 - zone_segmentation 연결(완)
  * MainApplication에 zone_seg_button 생성하여 zone_segmentation.py 연결
 - MainApplication의 file_system 객체에서 선택한 파일을 zone_segmentation으로 바로 받는 작업중
 - file_list()의 wrapper1 객체 가운데 정렬

[file_system.py]
1. file_system 모듈화(완)
 - file_system의 file_list를 함수로 분리(file_list()). 다른 부분에도 활용할 수 있도록 모듈화
  * file_data()는 자주 쓰지 않으므로, MainApplication에서 생성하여 file_list()의 wrapper1 객체로 연결

2. file_system Layout 작업중

3. 기타
 - Column 클릭시 오름차순/내림차순 구현(북마크 참고)
  * https://stackoverflow.com/questions/55268613/python-tkinter-treeview-sort-tree
 - 파일 선택 후 빈 공간 클릭시 하이라이트 해제(작업중)

[zone_segmentation.py]
1. 내부 UI 수정

[기타]
1. comp_file_system.py/comp_zone_segmentation.py는 백업 파일