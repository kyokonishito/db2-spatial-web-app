import json
import logging
from sqlalchemy import text
log_fmt = '%(asctime)s- %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_fmt, level=logging.DEBUG)


class Db2dataTool:
    engine = None
    table_name = None
    sql_str_getloc = "SELECT ST.NAME, ST.CAPACITY, ST_X(ST.GEO_POINT) LON, ST_Y(ST.GEO_POINT) LAT, "+ \
    "ST_Distance(ST_Point ({}, {},  2011), ST.GEO_POINT, 'METER') DIST " + \
    "FROM {} ST " + \
    "WHERE ST_Distance(ST_Point ({}, {},  2011), ST.GEO_POINT, 'METER') <={} " + \
    "ORDER BY DIST"
    
    def __init__(self, engine, table_name):
        self.engine = engine
        self.table_name = table_name
        

    def __handleError(self, msg):
        logging.error(msg)
        result = {}
        result['status'] = 'ERROR'
        result['message'] = msg
        return json.dumps(result)

    def __checkParm(self, parm):
        try:
            float(parm)  # 文字列を実際にfloat関数で変換してみる
        except ValueError:
            return False
        else:
            return True

    def getData(self, lat, lon, dist):
         
        if not self.__checkParm(lat):
            return self.__handleError("緯度が有効な数字ではありません")
        if not self.__checkParm(lon):
            return self.__handleError("経度が有効な数字ではありません")
        if not self.__checkParm(dist):
            return self.__handleError("距離が有効な数字ではありません")



        try:
            connection = self.engine.connect()
        except Exception as e:
           return self.__handleError(str(e))
        sql = self.sql_str_getloc.format(lon, lat, self.table_name ,lon, lat, dist)
        print(sql)
        result = {}
        result['sql']=sql

        try:
            res = connection.execute(text(sql))
        except Exception as e:
            return self.__handleError(str(e))
        else:
            rows = res.fetchall()
            result['count'] =  len(rows)
            if result['count']  > 0:
                t_rows = [tuple(row) for row in rows]
                resultdata = {}
                resultdata['data'] = t_rows[0:100]
                result['message'] = resultdata
            else:
                result['message'] = "No Results"

            result['status'] = 'SUCCESS'

        finally:
            connection.close()      
        
        return json.dumps(result)

