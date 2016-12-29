#coding=utf-8
#抓取所有用户信息
import requests
import re
import sys
import MySQLdb
import os
import cjson
from time import sleep

threadnum = os.popen("ps aux | grep zhihuuserdetail -wc")
tnum = threadnum.read()
if int(tnum) > 3:
	print int(tnum)
	threadnum.close()
	sys.exit()
threadnum.close()

reload(sys)
sys.setrecursionlimit(300000)
sys.setdefaultencoding('utf-8')

class Zhihuuserdetail():
	num = 0
	allurls = {}
	allkey = {}

	def __init__(self):
		self.conn = MySQLdb.connect(
		    host = 'localhost',
		    port = 3306,
		    user = 'root',
		    passwd = '',
		    db = 'zhihudata',
		    charset = 'UTF8',
		)
		self.cur = self.conn.cursor()

	def getusers(self):
		try:
			sql = "select id,urltoken from zhihuuser where ISNULL(updatetime)"
			self.cur.execute(sql)
			results = self.cur.fetchall()
			for row in results:
				self.allurls[row[0]] = str(row[1])
			self.allkey = sorted(self.allurls.keys())
			self.requestdata(self.allurls[self.allkey[self.num]],self.allkey[self.num])
		except:
		   print "Error: unable to fecth data"

	def requestdata(self, usertoken, index):
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, sdch, br',
			'Accept-Language':'zh-CN,zh;q=0.8',
			'Connection':'keep-alive',
			'Cookie':'d_c0="ACBAa0ulmQqPTrVdyqFVe4G3LZ6CH8jmoaY=|1474889679"; _za=f32d2598-ba48-4298-85a4-16e7340c1cbd; _zap=e443a29c-13bc-4b4c-b6da-eee8c79f9427; q_c1=0baee564d3ac4a2a8c9475421ea21cea|1480517926000|1474889678000; a_t="2.0ABCMGsD67QgXAAAAHnJnWAAQjBrA-u0IACBAa0ulmQoXAAAAYQJVTVv6ZVgA6p_ZDJz1uQrJ-BtGz-pkwRGsHOI1nVAvDpSKoAhp-PaBZSjsAyx3Yg=="; _xsrf=593fb28c35c18bbddefa41f1105b3441; s-t=autocomplete; s-q=%E7%BB%B4%E6%9D%83%E9%AA%91%E5%A3%AB; s-i=1; sid=ckm9ktg8; l_n_c=1; l_cap_id="OWMwYmQwNDE0MGJkNGU2Y2I0MmQ3YmE3ZTE5NjUzMzQ=|1482926304|b2f5881df17fc0fc81175706d7a57ef0cf7b7cb0"; cap_id="NDYxNWIwYThjZDM0NDE1ODhlNjAwNTY1M2YxMTkyY2Q=|1482926304|0e12270fb9837fb658bd6a4115eb19def8933a40"; r_cap_id="NTY0MjQxOTQ0MTBlNDlhNTkwM2QzZDlkN2ExMGRmNzY=|1482926305|21e93432a7b427c0b26ea0f1274e2ef3c516f5c4"; login="ZWMwOTRjYTY2OWIxNDM2Njg0ZWExZDE0ZTg2MmY3YTU=|1482926338|5be9589ec1bb4ce6222a8b9368f45fc807de7ab8"; __utma=51854390.318663902.1482395678.1482915026.1482926305.7; __utmb=51854390.20.9.1482926461958; __utmc=51854390; __utmz=51854390.1482750899.5.5.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.100--|2=registration_date=20161221=1^3=entry_date=20160926=1; z_c0=Mi4wQUdCQ0dCdGVDQXNBSUVCclM2V1pDaGNBQUFCaEFsVk5ERGFMV0FDVTQtWWh1aVVoVmUxb3pYbVdLUmlHWFlnVVVR|1482926473|5f2a7f4fe4ecd615aca509c033d38918430730a0',
			'Host':'www.zhihu.com',
			'Upgrade-Insecure-Requests':'1',
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
		}
		userurl = 'https://www.zhihu.com/people/' + usertoken + '/following'
		try:
			result = requests.get(userurl, headers = headers, timeout = 60)
			content = result.text
			content = content.replace('&quot;','"')
			content = content.replace('\\\\','')
			data = re.findall(u'data-state="(.*?)" data-config',content) 
			if len(data):
				b = cjson.decode(data[0].encode('utf-8').decode('utf-8'))
				tmp = b['entities']['users'][usertoken.encode('utf-8').decode('utf-8')]
				sql = "update zhihuuser set name='" + tmp['name'] + "',description='" + tmp['description'] + "',headline='" + tmp['headline'] + "',sex='" + str(tmp['gender']) + "',answer='" + str(tmp['answerCount']) + "',share='" + str(tmp['articlesCount']) + "',question='" + str(tmp['questionCount']) + "',favorite='" + str(tmp['favoriteCount']) + "',address='" + (tmp['locations'][0]['name'] if len(tmp['locations']) != 0 else u'') + "',business='" + (tmp['business']['name'] if tmp.has_key('business') and tmp['business'] != None else u'') + "',company='" + (tmp['employments'][0]['company']['name'] if len(tmp['employments']) and tmp['employments'][0].has_key('company') != 0 else u'') + "',profession='" + (tmp['employments'][0]['job']['name'] if len(tmp['employments']) != 0 and tmp['employments'][0].has_key('job') else u'') + "',school='" + (tmp['educations'][0]['school']['name'] if len(tmp['educations']) != 0 and tmp['educations'][0].has_key('school') else u'') + "',major='" + (tmp['educations'][0]['major']['name'] if len(tmp['educations']) != 0 and tmp['educations'][0].has_key('major') else u'') + "',voteup='" + str(tmp['voteupCount']) + "',thanked='" + str(tmp['thankedCount']) + "',favorited='" + str(tmp['favoritedCount']) + "',following='" + str(tmp['followingCount']) + "',follow='" + str(tmp['followerCount']) + "',followingtopic='" + str(tmp['followingTopicCount']) + "',followingcolumns='" + str(tmp['followingColumnsCount']) + "',followingquestion='" + str(tmp['followingQuestionCount']) + "',followingfavlists='" + str(tmp['followingFavlistsCount']) + "' where id='" + str(index) + "'"
				self.cur.execute(sql)
				self.conn.commit()
				del b
				del sql
				del tmp
			self.num = self.num + 1
			print index
			del result
			del content
			del data
			self.requestdata(self.allurls[self.allkey[self.num]],self.allkey[self.num])
		except Exception, e:
			print str(e)
			pass

if __name__ == '__main__':
	zhihuuserdetail = Zhihuuserdetail()
	zhihuuserdetail.getusers()
	
