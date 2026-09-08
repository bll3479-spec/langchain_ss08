#주어진 txt를 파싱
#리뷰에 대한 댓글이 생성되도록(해적 메일 참고) 루틴 생성.
#10개로만 실행할 것.(토큰 아끼시오)
#main.py를 실행했을 때 각 리뷰에 대한 리플이 자동으로 생성되도록.
#원 데이터 링크:https://drive.google.com/file/d/1WnHJ7JpsAjg7ShrONua-AA2iCshjZ_Mo/view?usp=drive_link

#권장방향
#1. ()라이브러리 사용해서 txt 파일 읽어오기
#2. 오늘 한 chain 함수를 이용해 댓글 분류(선택사항) -> 긍정/부정
#3. chain 함수를 이용해 댓글에 대한 답글 생성 -> (+) 프롬프팅에 페르소나 부여.