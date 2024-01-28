'''
계좌정보 조회? pykis에서 다해줌. 주식 정보까지 제공해줌. ex) 예수금, 평가금, 손익 및 보유 주식 등...
니가 할건 json으로 변환해서 mongodb에 쑤셔박는것 뿐임
'''


# 계좌 스코프 생성
account = kis.account(ACCOUNT_NO) # 계좌번호 ex) 50071022-01 또는 5007102201
# 일별주문내역 조회, 정정가능주문 조회 등도 존재함.
# 매수 주문
order = account.buy(
    # 종목 코드
    '000660',
    # 주문 수량
    qty=436,
    # 주문 단가
    unpr=89300,
)
# 시장가 매수 주문
order = account.buy(
    # 종목 코드
    '000660',
    # 주문 수량
    qty=436,
    # 주문 단가 (시장가 주문이므로 0)
    unpr=0,
    dvsn='시장가'
)

# 매도 주문, 나머지는 매수와 동일
order = account.sell(
    # 종목 코드
    '000660',
    # 주문 수량
    qty=436,
    # 주문 단가
    unpr=89300,
)

# 주문 취소
order = account.cancel(order)
# 주문 번호를 이용한 주문 취소
order = account.cancel(KisStockOrderBase(
    # KRX주문조직번호
    '06010', 
    # 주문번호
    '0001569157'
))

# 주문 정정
order = account.revise(
    # 기존 주문
    order,
    # 주문 수량 None이면 전량
    None,
    # 주문 단가
    89100
)
# 주문 번호를 이용한 주문 정정
order = account.revise(
    # 기존 주문
    KisStockOrderBase(
        # KRX주문조직번호
        '06010', 
        # 주문번호
        '0001569157'
    ),
    # 주문 수량 None이면 전량
    None,
    # 주문 단가
    89100
)