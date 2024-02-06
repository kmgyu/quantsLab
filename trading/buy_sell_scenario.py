import os
from dotenv import load_dotenv
from pathlib import Path
from pykis import *
from prettytable import PrettyTable
from db_handler.mongodb_handler import MongoDBHandler
import datetime
import time

"""
    https://github.com/Soju06/python-kis
    해당 모듈은 sqlite를 이용함. mongodb 안쓴다.
    json과 유사한 딕셔너리 형태로 저장하여 mongodb 핸들러를 사용할 수 있게 바꿔주자....
    수정해주엇다. 그래서 이제 뭐함?
    스케쥴러는 코드구현 안했음. 싸가지없어
"""

load_dotenv()

ACCOUNT_NO = os.environ.get('ACCOUNT_NO')
print(ACCOUNT_NO)
kis = PyKis(
    # 앱 키  예) Pa0knAM6JLAjIa93Miajz7ykJIXXXXXXXXXX
    # appkey=os.environ.get('APPKEY'),
    appkey='PSTHN47hUKYoIslXPaIjUpm7Bw8uj9uTQN7c',
    # 앱 시크릿  예) V9J3YGPE5q2ZRG5EgqnLHn7XqbJjzwXcNpvY . . .
    # appsecret=os.environ.get('APPSECRET'),
    appsecret='KIaC0HmcC73oZMc+0YHxCTDcse9gbq6j5ckplU5GNEDu4XIST6QBEWG4UM+BQ+H/Qvm4pLWYsX7xQKxMiMD611AsEwAb+qE85TXVmGwlnRoU7lPnMzXu8KaytvioJKrj913XyH4Q+T6erXlJ0gAHoU4oJkJbMhUqzMEra14gRVmQC2QSOO8=',
    # 가상 계좌 여부
    virtual_account=True,
    
)
mongodb = MongoDBHandler()

account = kis.account('50101522-01')



ACCOUNT_NO = os.environ.get('ACCOUNT_NO')
print(ACCOUNT_NO)
kis = PyKis(
    # 앱 키  예) Pa0knAM6JLAjIa93Miajz7ykJIXXXXXXXXXX
    # appkey=os.environ.get('APPKEY'),
    appkey='PSTHN47hUKYoIslXPaIjUpm7Bw8uj9uTQN7c',
    # 앱 시크릿  예) V9J3YGPE5q2ZRG5EgqnLHn7XqbJjzwXcNpvY . . .
    # appsecret=os.environ.get('APPSECRET'),
    appsecret='KIaC0HmcC73oZMc+0YHxCTDcse9gbq6j5ckplU5GNEDu4XIST6QBEWG4UM+BQ+H/Qvm4pLWYsX7xQKxMiMD611AsEwAb+qE85TXVmGwlnRoU7lPnMzXu8KaytvioJKrj913XyH4Q+T6erXlJ0gAHoU4oJkJbMhUqzMEra14gRVmQC2QSOO8=',
    # 가상 계좌 여부
    virtual_account=True,
    
)
mongodb = MongoDBHandler()

account = kis.account('50101522-01')

def trading_scenario(code_list):
    pass

# 장 시작하면 유닛테스트 돌릴때 이거쓰기
def buy_order():
    # 종목 미보유시 매수

    code = '011150'
    stock = kis.stock(code)
    price = stock.price()
    qty = 10
    # 최대 매수 가능 수량
    # qty = amount.max_buy_qty
    order = account.buy(
    # 종목 코드
    code,
    # 주문 수량
    qty=qty,
    unpr=price.stck_prpr-300 #현재가 -300원 매수
    )
    
    print(order.message)
    order_doc = {
        "주문번호":order.odno,
        "주문수량":qty,
        "단축코드":code,
        "status":"buy_ordered",
    }
    mongodb.insert_item(order_doc, 
                    "quantsLab", "order")
    # print("current_price", unpr)

def sell_order():
    sell_order_list = set(mongodb.find_items({"status": "buy_ordered"}), "quantsLab", "order") #이중에 존재하는 것들만 판매하기.
    # for order in sell_order_list:
    #     if order[]
    balance = account.balance_all()
    
    # 시장가 매도
    for stock in balance.stocks:
        # if stock.pdno not in sell_order_list: continue
        if stock.evlu_erng_rt > 2: #수익률 2%이상일 시 매도
            order = account.sell(
                code = stock.pdno,
                qty=stock.hldg_qty,
                unpr=0,
                dvsn='시장가'
            )
        order_doc = {
            "주문번호":order.odno,
            "주문수량":stock.hldg_qty,
            "단축코드":stock.pdno,
            "status": "sell_ordered"
        }
        mongodb.insert_item(order_doc, 
                        "quantsLab", "order")

def check_account():
    # 주문 체결 확인을 위한 계좌 조회
    table = PrettyTable(field_names=[
            '상품번호',
            '상품명',
            '보유수량',
            '매입금액',
            '현재가',
            '평가손익율',
            '평가손익',
        ],
        align='r',
    )

    balance = account.balance_all()

    print(f'예수금: {balance.dnca_tot_amt:,}원 평가금: {balance.tot_evlu_amt:,} 손익: {balance.evlu_pfls_smtl_amt:,}원')

    for stock in balance.stocks:
        table.add_row([
            stock.pdno,
            stock.prdt_name,
            f'{stock.hldg_qty:,}주',
            f'{stock.pchs_amt:,}원',
            f'{stock.prpr:,}원',
            f'{stock.evlu_pfls_rt:.2f}%',
            f'{stock.evlu_pfls_amt:,}원',
        ])

    print(table)
    
    
