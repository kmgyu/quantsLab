from pymongo import MongoClient
from pymongo.cursor import CursorType
import configparser
"""
    오류메시지 중복이 많음.
    리팩토링 시 이 부분이 작성하기 비효율적이니 오류코드같은걸 추가로 만들고 지정한 오류코드나오게 설정하기..
    unittest (138p) 생략함.
"""
class MongoDBHandler:
    """
    pymongo 래핑 클래스
    """
    def __init__(self):
        """
        config.ini 파일에서 MongoDB 접속 정보를 로딩한다.
        접속 정보를 이용해 MongoDB 접속에 사용할 _client를 생성
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        host = config['MONGODB']['host']
        port = config['MONGODB']['port']
        
        self._client = MongoClient(host, int(port))
    
    def insert_item(self, data, db_name = None, collection_name = None):
        """
        :param data: dict: 문서를 받다
        :param db_name: str: MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
        :param collection_name: str: 데이터베이스에 속하는 컬렉션 이름을 받는다.
        :return inserted_id: str: 입력 완료된 문서의 ObjectID 반환
        :raises Exception: 매개변수 db_name과 collection_name이 없으면 예외 처리
        """
        if not isinstance(data, dict):
            raise Exception("data type should be dict")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].insert_one(data).inserted_id
    
    def insert_items(self, datas, db_name = None, collection_name = None):
        """
        :param datas: dict: 문서를 받다
        :param db_name: str: MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
        :param collection_name: str: 데이터베이스에 속하는 컬렉션 이름을 받는다.
        :return inserted_ids: 입력 완료된 문서의 ObjectID list 반환
        :raises Exception: 매개변수 db_name과 collection_name이 없으면 예외 처리
        """
        if not isinstance(datas, dict):
            raise Exception("datas type should be dict")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].insert_one(datas).inserted_ids
    
    def find_item(self, condition=None, db_name=None, collection_name = None):
        # 134p 참고
        if condition is None or not isinstance(condition, dict):
            condition = {}
        if db_name is None or collection_name is None:
            raise Exception("need to param db_name, collection_name")
        return self._client[db_name][collection_name].find_one(condition)
    
    def find_items(self, condition=None, db_name=None, collection_name = None):
        if condition is None or not isinstance(condition, dict):
            condition = {}
        if db_name is None or collection_name is None:
            raise Exception("need to param db_name, collection_name")
        return self._client[db_name][collection_name].find(condition, no_cursor_timeout=True, cursor_type = CursorType.EXHAUST)
    
    def delete_items(self, condition=None, db_name=None, collection_name = None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("Need to condition")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].delete_many(condition)
    
    def update_item(self, condition=None, update_value=None, db_name=None, collection_name = None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("Need to conditoin")
        if update_value is None:
            raise Exception("Need to update value")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].update_one(filter=condition, update = {"$set": update_value}, upsert=True)
    
    def update_items(self, condition=None, update_value=None, db_name=None, collection_name = None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("Need to conditoin")
        if update_value is None:
            raise Exception("Need to update value")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].update_many(filter=condition, update=update_value)
    
    def aggregate(self, pipeline = None, db_name = None, collectoin_name=None):
        if pipeline is None or not isinstance(pipeline, dict):
            raise Exception("Need to pipeline")
        if db_name is None or collectoin_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collectoin_name].aggregate(pipeline)
    
    def text_search(self, text=None, db_name=None, collection_name=None):
        if text is None or not isinstance(text, str):
            raise Exception("Need to text")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].find({"$text": {"$search": text}})