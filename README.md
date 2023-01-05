[index.py 작업중]
1. file_system 연결(작업 중)
 - file_system 모듈화와 연결 작업

[file_system.py 작업중]
1. file_system 모듈화 작업중
 - file_system의 파일 목록/데이터 보기를 나눠서 다른 부분에도 활용할 수 있도록 모듈화 중

2. file_system Layout 작업중

3. 통합 UI 구축 중
 - zone_segmentation 연결(완)

4. 기타
 - Column 클릭시 오름차순/내림차순 구현(북마크 참고)
  * https://stackoverflow.com/questions/55268613/python-tkinter-treeview-sort-tree
 - Name column 텍스트에 밑줄 추가
  * 개별 column에 tag 적용할 수 없어 적용 X(tkinter 모듈 한계)
 - 파일 선택 후 빈 공간 클릭시 하이라이트 해제(작업중)

[zone_segmentation.py]
1. zone_segmentation을 팝업창으로 열었을 때, 최상위 창이 되도록 수정(완)
  * Toplevel(master).grab_set()으로 항상 최상위 창이 되도록 수정
 - file dialog 열었을 때 zone_segmentation이 parent가 되도록 함
  * askopenfiles, askdirectory의 argument에서 parent = self.master로 설정

2. 내부 UI 수정

[기타]
1. comp_file_system.py/comp_zone_segmentation.py는 백업 파일 