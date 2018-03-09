# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/09/28
'''

import sys
sys.path.append(".")
from common.logger import logger
import backstage_configuration_config as pc
from backstage_configuration.storage import business_storage_init

'''
本脚本功能：
    1. ***_sql实现sql语句组装（如果表的字段名有更改，这里头有些是要改的）+执行sql操作
    2. select_sql需实现外传参数的处理(select_limit or select_limit)，规范化后再进入.
此脚本调用（测试）方法and各表传值规范： 
    1. 请参考..test.batch_case.business_storage_op_local_recheck.py
'''

class StorageOperation(object):
    def __init__(self, tag):
        self.tag = tag# ref to [servers_db] in [params_config]
        self.sql_init = business_storage_init.SqlInit()
        self.conn, self.cursor = self.sql_init.set_db(tag)
        self.table_base = pc.table_base#pc.table_mapping.keys()
        self.table_main = pc.table_main

    def set_table(self, table):
        '''
        1. 建表时才需要考虑不同服的同名表的字段差异；表操作时，目前对差异的处理是通用的。
            # 目前三个服有差别的字段是：测试服正式服主表有local_id，"semantic_conf_memory_local"有sync_status。
        2. 后面也许会有set tables，考虑用于如下情况：
            "DELETE t1,t2 from t1 LEFT JOIN t2 ON t1.id=t2.id WHERE t1.id=25";
            "delete t1,t2 from table_name as t1 left join table2_name as t2 on t1.id=t2.id where table_name.id=25".
        '''
        self.table = table
        if self.sql_init.check_table_exist(self.table) == False:
            _table = self.table + "_" + str(self.tag)
            create_table_sql = business_storage_init.create_table_dict.get(_table, "")
            self.sql_init.create_table(create_table_sql=create_table_sql)

    def select_sql(self, select_str):
        result = "未能正确解析传入的值"
        if select_str != "":
            # print("select_sql: {}".format(select_str))
            logger.info("select_sql: {}".format(select_str))
            try:
                self.cursor.execute(select_str)
                result_1 = self.cursor.fetchall()
                logger.info("select result: {}".format(result_1))
                if result_1 or result_1 == ():
                    result = result_1
            except Exception as e:
                logger.warning("error when select: {}".format(e))
                # print("error when select: {}".format(e))
                result = result + ": " + str(e)
        return result

    def insert_sql(self, **kw):
        '''
        关于self.table not in self.table_base，外层逻辑调用这块功能前需实现的：
            bg_id是外键，要判断在主表中是否已存在或由主表的结果返回得到。
            a_sentence is from a_sentence_list，调用前先套层遍历。
        '''
        insert_sql = ""
        if self.table in self.table_base:
            insert_str = "INSERT INTO " + self.table + " (id, "
            for i in kw.keys():
                insert_str = insert_str + i + ", "
            insert_str = insert_str + "save_time) VALUE (NULL, "
            for j in kw.values():
                if isinstance(j, str) or isinstance(j, unicode):
                    insert_str = insert_str + "\'" + j + "\', "
                else:
                    insert_str = insert_str + str(j) + ", "
            insert_sql = insert_str + "now())"

        result = "未能正确解析传入的值"
        if insert_sql != "":
            logger.info("insert_data_sql: {}".format(insert_sql))
            try:
                self.cursor.execute(insert_sql)
                self.conn.commit()
                self.cursor.execute("select @@IDENTITY")
                # get last id
                result = int(self.cursor.fetchall()[0][0])
                logger.info("insert result(id): {}".format(result))
            except Exception as e:
                logger.warning("error when insert: {}".format(e))
                # print("error when insert: {}".format(e))
                result = result + ": " + str(e)
        return result

    def update_sql(self, **kw):
        # ref to [bg_id] or [id]
        update_sql = ""
        if self.table == self.table_main:
            us = "update " + self.table + " set "
            for i in kw:
                if i not in ['bg_id', 'save_time']:
                    if isinstance(kw[i], str) or isinstance(kw[i], unicode):
                        us = us + "{}=\'{}\', ".format(i, kw[i])
                    else:
                        us = us + "{}={}, ".format(i, kw[i])
            update_sql = us + 'save_time=now() where id={}'.format(kw['bg_id'])
            if 'save_time' in kw.keys():
                # 这是只用于conf_save的
                update_sql = update_sql.replace("save_time=now()","").replace(",  where", "  where")

        elif self.table in self.table_base:
            if 'id' in kw.keys():
                us = "update " + self.table + " set "
                for i in kw:
                    if i != 'id':
                        if isinstance(kw[i], str) or isinstance(kw[i], unicode):
                            us = us + "{}=\'{}\', ".format(i, kw[i])
                        else:
                            us = us + "{}={}, ".format(i, kw[i])
                update_sql = us + 'save_time=now() where id={}'.format(kw['id'])
            else:
                # 这是只用于conf_save的
                us = "update " + self.table + " set "
                for i in kw:
                    if i not in ['bg_id', 'a_sentence', 'para_sentence']:
                        if isinstance(kw[i], str) or isinstance(kw[i], unicode):
                            us = us + "{}=\'{}\', ".format(i, kw[i])
                        else:
                            us = us + "{}={}, ".format(i, kw[i])
                us = us + " where bg_id={} and ".format(kw["bg_id"])
                us = us + " a_sentence=\'{}\'".format(kw["a_sentence"]) if "a_sentence" in kw.keys() \
                    else us + " para_sentence=\'{}\'".format(kw["para_sentence"])
                update_sql = us.replace(",  where", " where")

        result = "未能正确解析传入的值"
        if update_sql != "":
            # print("update_data_sql: {}".format(update_sql))
            logger.info("update_data_sql: {}".format(update_sql))
            try:
                line_count = self.cursor.execute(update_sql)
                self.conn.commit()
                result = line_count#影响行数
            except Exception as e:
                logger.warning("error when update: {}".format(e))
                # print("error when update: {}".format(e))
                result = result + ": " + str(e)
        return result

    def delete_sql(self, **kw):
        delete_sql = ""
        if self.table == self.table_main and 'bg_id' in kw.keys():
            bg_id = kw['bg_id']
            delete_sql = "DELETE FROM " + self.table + " WHERE id={}".format(bg_id)
        elif self.table in self.table_base:
            delete_sql = "DELETE FROM " + self.table + " WHERE " + str(kw.keys()[0]) + "=" + str(kw.values()[0])

        result = "未能正确解析传入的值"
        if delete_sql != "":
            # print("delete_data_sql: {}".format(delete_sql))
            logger.info("delete_data_sql: {}".format(delete_sql))
            try:
                self.cursor.execute(delete_sql)
                self.conn.commit()
                result = True
            except Exception as e:
                logger.warning("error when delete: {}".format(e))
                # print("error when delete: {}".format(e))
                result = result + ": " + str(e)
        return result

    def select_limit(self, select_tuple=None, select_origin=""):
        '''
        select_tuple单限制查询： 目前包括根据id或句子查询两种应用场景。
        select_tuple = (column_name, column_value)
        sth about column_name: so only column name here, no as "bg_id".
        select_origin用于手动写入sql语句。
        '''
        if select_origin != "":
            select_str = select_origin
        else:
            select_str = ""
            if select_tuple == None:
                select_str = "select * from " + self.table
            elif isinstance(select_tuple, tuple) and self.table in self.table_base:
                if isinstance(select_tuple[1], int):
                    select_str = "select * from " + self.table + " where " + select_tuple[0] + "=" + str(select_tuple[1])
                else:
                    select_str = "select * from " + self.table + " where " + select_tuple[0] + "='" + str(select_tuple[1]) + "'"
        return self.select_sql(select_str)

    def select_limits(self, select_dict):
        '''
        如果是加普通值做限制，这里不需要做调整。
        '''
        select_str = ""
        if select_dict != {}:
            select_str = "select * from (select * from " + self.table_main + " "
            f = 0
            for i in select_dict:
                if i != "limit_count" and i != "limit_page":
                    if f == 0:
                        select_str = select_str + " where "
                        f = 1
                    else:
                        select_str = select_str + " and "
                    if isinstance(select_dict[i], str) or i == "backward_time":
                        select_str = select_str + i + "='" + select_dict[i] + "'"
                    else:
                        select_str = select_str + i + "=" + str(select_dict[i])
            select_str = select_str + " limit " + str(select_dict["limit_count"]) + ")" if "limit_count" in select_dict else select_str + ")"
            select_str = select_str.replace("backward_time=", "save_time>=")
            select_str = select_str + "as tb_1 order by save_time desc "
            select_str = select_str + " limit " + select_dict["limit_page"] if "limit_page" in select_dict else select_str
        return self.select_sql(select_str)


