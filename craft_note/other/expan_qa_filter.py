# -*- coding: utf-8 -*-
import time
import json
import os,os.path
import datetime
import requests

store_url = "http://172.19.1.126:9051/corpus"
file_path = os.path.join(os.path.dirname(os.getcwd()), "k_log\\",)
time_tag = datetime.datetime.now().strftime('_%m-%d_%H-%M-%S')
orig_path = file_path + "qalogc_k-2.txt"
file_1 = file_path + "expan_result" + time_tag + '.json'
file_2 = file_path + "expan_result" + time_tag + '_irreg.json'
# todo: 可以考虑把json改py，然后直接赋值读
# with open(file_path + "expan_result_12-27_10-23-34.json", "r") as f:
#     print f.read()
#     print json.loads(f.read(), encoding='utf-8')#, ensure_ascii=False)
#     # print a_dict

def get_batch(path):
    '''
    过滤掉第三点，详情如下：
    1. [一问n答]"log main]nomsolo_semtic org|modif|ra" 或者 [n答]"[log my] arg" 通常来自文件"3.jingque.txt"
    2. [n答]"log my] code77" 通常来自文件"2.pianduan.txt"
    3. 下面这四个跟上面两点重复了，暂时忽略：
    [log main]nomsolo_semtic moreway
    [log main]nomsolo_semtic nowr
    [log main]nomsolo_semtic nowr|ccnn|rescc
    [log main]searchpart code77-2
    '''
    batch_all = []
    batch_temp = []
    print path
    with open(path,"rb") as f:
        for line in f.readlines():#[-270:]:
            # print line
            if "******" in line and batch_temp != []:
                if "******" in batch_temp[0]:
                    batch_temp = batch_temp[1:]
                batch_all.append(batch_temp)
                batch_temp = []
            elif line == "\r\n" or "[log main]nomsolo_semtic moreway" in line or "[log main]nomsolo_semtic nowr" in line or "[log main]nomsolo_semtic nowr|ccnn|rescc" in line or "[log main]searchpart code77-2" in line:
                continue
            else:
                batch_temp.append(line)
    return batch_all

def filter_batch(batch_temp):
    '''
    解决以下几类问题，第1至3点参见函数get_batch：
    4. 假如第一点跟第二点为空，那么就跳过，因为一问一答已经有了。(len of them are 1)
    yes5. 答句为空的跳过，因为说明打分很低；答句带“function”的跳过；去掉末尾的“<sg>”及后面内容；去掉开头的“<train>”；跳过"这个我还不会，正在努力学习！"or"答案太多了"开头的
    6. 3精确没有被放到问答集的另外补上。
    yes7. 跳过走记忆的问句，如“你记得什么？”
    '''
    q_list = []
    a_list = []
    irregular_data = []
    for line in batch_temp:
        print line
        if "log main]output:" in line and len(line.split("log main]output:"))>1:
            output = line.split("log main]output:")[1].replace("\n","").replace("\r","")
            if output in ["", " "] or len(output) <= 1:
                return []
            elif "function" in output:
                return []
            elif "这个我还不会，正在努力学习！" in output or "答案太多了" in output:
                return []
            else:
                output = output[1:] if output[0] == " " else output
                output = output.split("<train>")[1] if len(output.split("<train>")) >1 else output
                output = output.split("<sg>")[0]
                if output in ["", " "] or len(output) <= 1:
                    return []
                else:
                    a_list.append(output)
        elif "log main]input:" in line and len(line.split("log main]input:"))>1:
            print line.split("log main]input:")
            input = line.split("log main]input:")[1].replace("\n","").replace("\r","")
            if input in ["", " "] or len(input) <= 1:
                return []
            elif "你记得什么" in input:
                return []
            input = input[1:] if input[0] == " " else input
            q_list.append(input)
        elif "log main]nomsolo_semtic org|modif|ra: " in line and len(line.split("log main]nomsolo_semtic org|modif|ra: "))>1:
            '''
            解析如下格式的数据：
            |log main]nomsolo_semtic org|modif|ra: 你家是哪里的|p_one_of("我家是一个美丽的天堂$spa你在的地方就是我的家啊$spa机器人云游四海，处处都是家，就是这么潇洒$spa我的家在银河系边缘")#作者:阮胜兰#分类:询问#审稿时间:20150815 |0.666666666666667
            |log main]nomsolo_semtic org|modif|ra: 你睡觉晚安|p_return("奥，那晚安啦")#类型:每日回复#时间：2015/11/14 |0.5
            '''
            qa_one2multi = line.split("log main]nomsolo_semtic org|modif|ra: ")[1].split("|")
            if len(qa_one2multi) > 1:
                que = qa_one2multi[0]
                q_list.append(que)
                if "p_one_of(" in qa_one2multi[1]:
                    ans_list = qa_one2multi[1].split("p_one_of(")[1].split("#")[0][1:-2].split("$spa")
                elif "p_return(" in qa_one2multi[1]:
                    ans_list = qa_one2multi[1].split("p_return(")[1].split("#")[0][1:-2].split("$spa")
                else:
                    ans_list = []
                a_list = a_list + ans_list
        elif "log my] arg" in line and len(line.split("log my] arg"))>1:
            '''
            解析如下格式的数据：
            [log my] arg: one_of("我家是一个美丽的天堂$spa你在的地方就是我的家啊$spa机器人云游四海，处处都是家，就是这么潇洒$spa我的家在银河系边缘","047944")
            [log my] arg: return("骂人可不是乖宝宝")
            '''
            # print line.split("log my] arg: ")[1]
            ans_list = []
            try:
                if "one_of(" in line.split("log my] arg: ")[1]:
                    ans_list = line.split("log my] arg: ")[1].split("one_of(")[1].split('"')[1].split("$spa")
                elif "return(" in line.split("log my] arg: ")[1]:
                    ans_list = line.split("log my] arg: ")[1].split("return(")[1].split('"')[1].split("$spa")
            except:
                pass
            a_list = a_list + ans_list
        elif "log my] code77" in line and len(line.split("log my] code77"))>1:
            '''
            解析如下格式的数据：
            [log my] code77: one_of("上今天的班，睡昨天的觉 上班就像旧时代的婚姻，明明不幸福还得长相厮守。 没有假日的时候，只能盼望着停电了 上午坚决不起床，下午坚决不上班，晚上坚决不睡觉 不知道为什么，每月总有那么几天，要加班 男人嘛，每个月总有那么三十几天，不想上班 如果太阳不出来了，我就不去上班了,如果出来了,我就继续睡觉")
            [log my] code77: if($input=~/你(.*?)啦/){my$an=$1;my$topic=plugin_userinfo::ext_topic($an);$topic=~s/(.*?) .*/$1/g;$topic=~s/ //g;;if(length($topic)==0){return;};my$cc=one_line_of(fact_match_n_userself($topic."可能会带来",10,"concept5"))||one_line_of(fact_match_n_userself($topic."可能会导致",10,"concept5"))||one_line_of(fact_match_n_userself($topic."会你",10,"concept5"))||one_line_of(fact_match_n_userself($topic."可能会引起",10,"concept5"))}
            [log my] code77: return(one_of("梦到小白哦 主人做个美美的梦 睡觉最舒服了晚安 主人睡香香亲亲主人 主人好梦 主人睡我也睡 一起睡觉吧 一起觉觉吧 拜拜亲爱的 晚安啦我亲爱的 晚安我的偶像 晚安我亲爱的主人"))
            '''
            ans_temp = line.split("log my] code77: ")[1]
            if "if" in ans_temp or "=~" in ans_temp:
                continue
            elif "return(one_of(" in ans_temp:
                ans_list = ans_temp.split("return(one_of(")[1][1:-3].split(" ")
                a_list = a_list + ans_list
            elif "one_of(" in ans_temp:
                ans_list = ans_temp.split("one_of(")[1][1:-2].split(" ")
                a_list = a_list + ans_list
        elif line == "\r\n" or line == "\n" or line == "[log my] pcode:\r\n" or line == "[log my] pcode: \n":
            continue
        else:
            irregular_data.append(line)
    print len(q_list), q_list
    print a_list
    if len(q_list) <= 1 and len(a_list) <= 1:
        return []
    a_list = filter_ans(q_list, a_list)
    return [q_list, a_list, irregular_data]

def filter_ans(q_list, a_list):
    # todo: 这里弄列表去重和元素中无效字符(function resout user_hobby ignore\")删除
    a_list_new = []
    for a in a_list:
        a.replace('''\"''', "").replace("。","")
        if "function" in a or "resout" in a or "user_hobby" in a or "ignore" in a:
            print "xixi", q_list[0]
            continue
        if a in ["", " "] or len(a) <= 1:
            continue
        a_list_new.append(a)
    a_list_new_2 = list(set(a_list_new))
    return a_list_new_2

def save2api(format_data):
    '''
    {
	"data": [
		{
			"src_sentence": [
				"我帮你关机得了"
			],
			"generalization": [],
			"response": [
				{
					"condition": {
						"user_gender": "1",
						"hupo_emotion": "3",
						"hupo_hunger": "5"
					},
					"answer": [
						{
							"answer": "是要睡觉了吗"
						}
					]
				}
			]
		}
	]
	}
    '''
    src_sentence = format_data[0]
    print src_sentence
    print "will save this and more: ", src_sentence[0]
    answer = []
    for a in format_data[1]:
        answer.append(dict(answer=a))
    req = dict(data=[dict(src_sentence=src_sentence, generalization=[], response=[dict(condition=dict(user_gender="1", hupo_emotion="3", hupo_hunger="5"), answer=answer)])])
    try:
        resp = requests.post(url=store_url, data=json.dumps(req))
        ans = json.loads(resp.text)
        tag = ans.get("result", "")
    except:
        tag = False
    if tag == True:
        pass
    else:
        print "error here: "
        for q in src_sentence:
            print q


if __name__ == "__main__":
    all_dict_1 = {}
    all_dict_2 = {}
    batch_all = get_batch(orig_path)
    print len(batch_all)
    for i, batch_temp in enumerate(batch_all):
        format_data = filter_batch(batch_temp)
        if len(format_data) > 1:
            all_dict_1[i] = format_data[:-1]
            all_dict_2[i] = format_data[-1]
            # if i >= 2830:
            # save2api(format_data)
        else:
            all_dict_1[i] = []
            all_dict_2[i] = []

    with open(file_1, 'w') as f:
        f.writelines(json.dumps(all_dict_1, ensure_ascii=False, indent=4))
        # f.write(json.dumps(all_dict_1, encoding='utf-8', ensure_ascii=False))
    with open(file_2, 'w') as f:
        f.writelines(json.dumps(all_dict_2, ensure_ascii=False, indent=4))
        # f.write(json.dumps(all_dict_2, encoding='utf-8', ensure_ascii=False))



