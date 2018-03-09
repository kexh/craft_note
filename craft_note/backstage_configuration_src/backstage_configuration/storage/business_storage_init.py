# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/10/20
'''
import sys
sys.path.append(".")
import MySQLdb
from common.logger import logger
# from common.settings import SETTING
import backstage_configuration_config as SETTING

'''
本脚本功能： 
1. 自跑时可以用于建表（包括了外键和id自增）；
    使用前请建好空的db：
    0: semantic_conf_memory
2. 外部调用时，用于数据库和表的初始化，并且可以用来检查某个数据库的某张表是否存在。
'''

# create table sql of db [semantic_conf_memory]
create_q_sentence_table = \
                "CREATE TABLE semantic_conf_memory.`amber_conf_q_sentence` (" \
                "  `id` int(11) NOT NULL AUTO_INCREMENT," \
                "  `save_time` datetime DEFAULT NULL," \
                "  `q_sentence` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "  `emotion_type` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "  `emotion_target` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "  `emotion_polar` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "  `m_intent_type` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "  `q_sentence_priority` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "  `sync_status` int(11) DEFAULT NULL," \
                "  PRIMARY KEY (`id`)" \
                ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"

create_a_sentence_table = \
                "CREATE TABLE semantic_conf_memory.`amber_conf_a_sentence` (" \
                "`id` int(11) NOT NULL AUTO_INCREMENT," \
                "`a_sentence` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "`favor_num` float DEFAULT NULL," \
                "`mood_num` float DEFAULT NULL," \
                "`apply_scene` int(11) DEFAULT NULL," \
                "`save_time` datetime DEFAULT NULL," \
                "`bg_id` int(11) DEFAULT NULL," \
                "PRIMARY KEY (`id`)," \
                "KEY `bg_id` (`bg_id`)," \
                "CONSTRAINT `a_bg_id` FOREIGN KEY (`bg_id`) REFERENCES `amber_conf_q_sentence` (`id`)" \
                ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"

create_para_sentence_table = \
                "CREATE TABLE semantic_conf_memory.`amber_conf_para_sentence` (" \
                "`id` int(11) NOT NULL AUTO_INCREMENT," \
                "`para_sentence` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL," \
                "`enable` int(11) DEFAULT NULL," \
                "`score` float DEFAULT NULL," \
                "`save_time` datetime DEFAULT NULL," \
                "`bg_id` int(11) DEFAULT NULL," \
                "PRIMARY KEY (`id`)," \
                "KEY `bg_id` (`bg_id`)," \
                "CONSTRAINT `para_bg_id` FOREIGN KEY (`bg_id`) REFERENCES `amber_conf_q_sentence` (`id`)" \
                ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"


create_table_dict = {
    "amber_conf_q_sentence_0": create_q_sentence_table,
    "amber_conf_a_sentence_0": create_a_sentence_table,
    "amber_conf_para_sentence_0": create_para_sentence_table
}


class SqlInit:
    def set_db(self, tag=0):
        '''
        tag的值现包括以下1种，其对应的数据库名称和在配置表的名字如下：
        0: semantic_conf_memory --- config.ini: mysql_db_bg_conf_name
        '''
        logger.info("set db tag to 0 here.")
        logger.info("db name: {}".format(SETTING.DB_NAME))
        self.conn = MySQLdb.connect(host=SETTING.DB_IP, user=SETTING.DB_USER,
                                    passwd=SETTING.DB_PWD, db=SETTING.DB_NAME,
                                    port=int(SETTING.DB_PORT),
                                    charset="utf8")
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def check_table_exist(self, table):
        self.cursor.execute("show tables")
        for row in self.cursor.fetchall():
            if table in row:
                return True
        return False

    def create_table(self, create_table_sql):
        try:
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            return True
        except Exception as e:
            return False

if __name__ == '__main__':
    import backstage_configuration_config as pc

    tags = [0]#, 1, 2]
    sql_init = SqlInit()
    for tag in tags:
        sql_init.set_db(tag)
        for table in pc.table_base:
            _table = table + "_" + str(tag)
            print _table
            if sql_init.check_table_exist(table) == False:
                create_table_sql = create_table_dict.get(_table, "")
                print create_table_sql
                sql_init.create_table(create_table_sql=create_table_sql)
    print "success"

