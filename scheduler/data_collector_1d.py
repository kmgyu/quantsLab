import os
from dotenv import load_dotenv
from pathlib import Path
from pykis import *
from prettytable import PrettyTable
from ..db_handler.mongodb_handler import MongoDBHandler
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

kis = PyKis(
    # 앱 키  예) Pa0knAM6JLAjIa93Miajz7ykJIXXXXXXXXXX
    appkey=os.environ.get('APPKEY'),
    # 앱 시크릿  예) V9J3YGPE5q2ZRG5EgqnLHn7XqbJjzwXcNpvY . . .
    appsecret=os.environ.get('APPSECRET'),
    # 가상 계좌 여부
    virtual_account=True,
)
mongodb = MongoDBHandler()

def collect_code_list():
    # 단축코드를 db에 추가
    for stock in kis.market.kospi.all():
        mongodb.update_item({"단축코드":stock.mksc_shrn_iscd}, 
                            {"단축코드":stock.mksc_shrn_iscd, 
                             "종목명":stock.hts_kor_isnm,
                             "표준코드": stock.stnd_iscd,
                             "매매수량단위": stock.frml_mrkt_deal_qty_unit,
                             "기업인수목적회사구분": stock.etpr_undt_objt_co_yn}, 
                            "quantsLab", "code_info")


def collect_stock_info():
    # 현재가 조회
    # 현재가 이외에도 조회 가능하다.
    code_list = mongodb.find_items({}, "quantsLab", "code_info")
    target_code = set([item["단축코드"] for item in code_list])
    today = datetime.datetime.today().strftime("%Y%m%d")
    collect_list = mongodb.find_items({"날짜":today}, "quantsLab", "price_info").distinct("code")
    for col in collect_list:
        target_code.remove(col)
    for code in target_code:
        stock = kis.stock(code)
        if not stock:
            print('주식 정보를 찾을 수 없습니다.')
            continue
        time.sleep(1)
        price = stock.price()
        # dict 형식으로 리턴
        result_price = {
            '단축코드':code,
            '전일대비율':price.prdy_ctrt,
            # '현재가':price.stck_prpr,
            '시가':price.stck_oprc,
            '최저가':price.stck_lwpr,
            '최고가':price.stck_hgpr,
            '전일대비':price.prdy_vrss,
            '전일대비거래량비율':price.prdy_vrss_vol_rate,
            '거래대금':price.acml_tr_pbmn,
            '날짜':today
        }
        mongodb.update_item(condition={'단축코드':code}, update_value=result_price,
                            db_name="quantsLab", collection_name="price_info")

if __name__ == '__main__':
    collect_code_list()
    collect_stock_info()

















# # 먼저 계좌 스코프를 생성한다.
# account = kis.account('73412122-01') # 계좌번호 ex) 50071022-01 또는 5007102201
# # 이제 잔고를 조회한다.
# balance = account.balance_all()

# # 결과를 출력한다.
# print(f'예수금: {balance.dnca_tot_amt:,}원 평가금: {balance.tot_evlu_amt:,} 손익: {balance.evlu_pfls_smtl_amt:,}원')

# # 테이블을 시각화 하기 위해 PrettyTable을 사용한다.

# table = PrettyTable(field_names=[
#         '상품번호', '상품명', '보유수량', '매입금액',
#         '현재가', '평가손익율', '평가손익',
#     ], align='r',
# )

# # 잔고를 테이블에 추가한다.
# for stock in balance.stocks:
#     table.add_row([
#         stock.pdno,
#         stock.prdt_name,
#         f'{stock.hldg_qty:,}주',
#         f'{stock.pchs_amt:,}원',
#         f'{stock.prpr:,}원',
#         f'{stock.evlu_pfls_rt:.2f}%',
#         f'{stock.evlu_pfls_amt:,}원',
#     ])

# print(table)


# 전종목 조회 코드
# for stock in kis.market.kospi.all():
#     print(stock.mksc_shrn_iscd, stock.hts_kor_isnm)