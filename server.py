from flask import Flask, request
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
from db_handler.mongodb_handler import MongoDBHandler
from predicting import predict
import datetime

# import os
# from dotenv import load_dotenv
# from pathlib import Path
# from pykis import *
# from prettytable import PrettyTable


app = Flask(__name__)
CORS(app)
api = Api(app)

# load_dotenv()

# kis = PyKis(
#     # 앱 키  예) Pa0knAM6JLAjIa93Miajz7ykJIXXXXXXXXXX
#     appkey=os.environ.get('APPKEY'),
#     # 앱 시크릿  예) V9J3YGPE5q2ZRG5EgqnLHn7XqbJjzwXcNpvY . . .
#     appsecret=os.environ.get('APPSECRET'),
#     # 가상 계좌 여부
#     virtual_account=True,
# )

# 이거 말고도 위험한지 판단가능한 데이터들이 매우 많이 있다. 그게 제일 중요하니.... 참고하도록...
# 데이터 콜렉터에 kis를 넣어야되나 서버에 넣어야되나?
code_hname_to_eng = {
    "단축코드": "code",
    "표준코드": "extend_code",
    "종목명": "name",
    "매매수량단위": "quantity",
    "기업인수목적회사구분": "is_spac"
}

price_hname_to_eng = {
    "단축코드": "code",
    "날짜": "date",
    "종가": "close",
    "시가": "open",
    "최고가": "high",
    "최저가": "low",
    "전일대비": "diff",
    "전일대비거래량비율": "trsc_diff_per",
    "거래대금": "trsc_value", #transaction amount
}


code_fields = {
    "code": fields.String,
    "extend_code": fields.String,
    "name": fields.String,
    "quantity": fields.Integer,
    "is_spac": fields.String,
    "uri": fields.Url("code")
}
 
code_list_short_fields = {
    "code": fields.String,
    "name": fields.String
} 
code_list_fields = {
    "count": fields.Integer,
    "code_list": fields.List(fields.Nested(code_fields)),
    "uri": fields.Url("codes")
}

price_fields = {
    "date": fields.Integer,
    "close": fields.Integer,
    "open": fields.Integer,
    "high": fields.Integer,
    "low": fields.Integer,
    "diff": fields.Float,
    "diff_type": fields.Integer
}

price_list_fields = {
    "count": fields.Integer,
    "price_list": fields.List(fields.Nested(price_fields)),
 }

order_hname_to_eng = {
    "주문번호": "order_no",
    "주문수량": "st_quantity",
    "단축코드": "code",
    "status": "status"
}

order_list_fields = {
    "order_no": fields.String,
    "st_quantity": fields.Integer,
    "code": fields.String,
    "status": fields.String
}

predict_fields = {
    "message": fields.String,
}

mongodb = MongoDBHandler()
#https://flask-restful.readthedocs.io/en/0.3.3/intermediate-usage.html#full-parameter-parsing-example

class Code(Resource):
    @marshal_with(code_fields)
    def get(self, code):
        result = mongodb.find_item({"단축코드":code}, "quantsLab", "code_info")
        if result is None:
            return {}, 404
        code_info = {}
        code_info = { code_hname_to_eng[field]: result[field] 
                        for field in result.keys() if field in code_hname_to_eng }
        return code_info

class CodeList(Resource):
    # 너무 많아서 렉거림ㅁ. 100개로 제한시켰다.
    @marshal_with(code_list_fields)
    def get(self):
        market = request.args.get('market', default="0", type=str)
        if market == "0":
            results = list(mongodb.find_items({}, "quantsLab", "code_info"))
        elif market == "1" or market == "2":
            results = list(mongodb.find_items({"시장구분":market}, "quantsLab", "code_info"))
        result_list = []
        for item in results:
            code_info = {}
            code_info = { code_hname_to_eng[field]: item[field] for field in item.keys() if field in code_hname_to_eng }
            result_list.append(code_info)
        return {"code_list" : result_list[:100], "count": len(result_list)}, 200

class Price(Resource):
    @marshal_with(price_list_fields)
    def get(self, code):
        today = datetime.datetime.now().strftime("%Y%m%d")
        default_start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        start_date = request.args.get('start_date', default=default_start_date.strftime("%Y%m%d"), type=str)
        end_date = request.args.get('end_date', default=today, type=str)
        results = list(mongodb.find_items({"단축코드":code, "날짜": {"$gte":start_date, "$lte":end_date}}, 
                                            "quantsLab", "price_info"))
        results.sort(key=lambda x:x["날짜"])
        result_object = {}
        price_info_list = []
        for item in results:
            price_info = { price_hname_to_eng[field]: item[field] for field in item.keys() if field in price_hname_to_eng } 
            price_info_list.append(price_info)
        result_object["price_list"] = price_info_list
        result_object["count"] = len(price_info_list)
        
        # print(results)
        print('get pricelist', start_date, end_date)
        
        return result_object, 200

class OrderList(Resource):
    @marshal_with(order_list_fields)
    def get(self):
        status = request.args.get('status', default="all", type=str)
        if status == 'all':
            result_list = list(mongodb.find_items({}, "quantsLab", "order"))
        elif status in ["buy_ordered", "buy_completed", "sell_ordered", "sell_completed"]:
            result_list = list(mongodb.find_items({"status":status}, "quantsLab", "order"))
        else:
            return {}, 404
        
        order_info_list = []
        for item in result_list:
            order_info = {order_hname_to_eng[field]: item[field] for field in item.keys() if field in order_hname_to_eng}
            
            order_info_list.append(order_info)
        
        return order_info_list, 200

class Prediction(Resource):
    @marshal_with(predict_fields)
    def get(self, code):
        message = predict(code)
        print(message)
        return {"message":message}, 200
        
    

api.add_resource(CodeList, "/codes", endpoint="codes")
api.add_resource(Code, "/codes/<string:code>", endpoint="code")
api.add_resource(Price, "/codes/<string:code>/price", endpoint="price")
api.add_resource(OrderList, "/orders", endpoint="orders")
api.add_resource(Prediction, "/codes/<string:code>/predict", endpoint="predict")

if __name__ == "__main__":
    app.run(debug=True)