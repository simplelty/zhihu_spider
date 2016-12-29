#coding=utf-8
#抓取所有用户信息
import requests
import re
import random
import json
import sys
import MySQLdb
import threading
import os
from time import sleep
import time

threadnum = os.popen("ps aux | grep zhihuuser.py -wc")
num = threadnum.read()
if int(num) > 3:
	print int(num)
	threadnum.close()
	sys.exit()
threadnum.close()

reload(sys)
sys.setrecursionlimit(300000)
sys.setdefaultencoding('utf-8')

class Zhihuuser():
	datanum = 1
	allurls = {}
	results = []

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
			sql = "select urltoken from zhihuuser"
			self.cur.execute(sql)
			self.results = self.cur.fetchall()
			self.datanum = len(self.results)
			for row in self.results:
				self.allurls[str(row[0])] = True
			self.main(self.results[random.randint(100, 20000)][0])
		except:
		   print "Error: unable to fecth data"

	def main(self, userurl):
		try:
			curnum = 0
			url = 'https://www.zhihu.com/api/v4/members/' + userurl + '/followers'
			headers = {
				'Accept':'*/*',
				'Accept-Encoding':'gzip, deflate, sdch, br',
				'Accept-Language':'zh-CN,zh;q=0.8',
				'authorization':'Bearer Mi4wQUdCQ0dCdGVDQXNBSUVCclM2V1pDaGNBQUFCaEFsVk5ERGFMV0FDVTQtWWh1aVVoVmUxb3pYbVdLUmlHWFlnVVVR|1482926473|5f2a7f4fe4ecd615aca509c033d38918430730a0',
				'Cache-Control':'max-age=0',
				'Connection':'keep-alive',
				'Host':'www.zhihu.com',
				'Referer':'https//www.zhihu.com/people/' + userurl + '/followers',
				'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
			}
			data = {
				'per_page' : 30,
				'include' : 'data[*].answer_count,articles_count,follower_count',
				'limit' : 30
			}
			data['offset'] = curnum
			sleep(random.uniform(0.5, 1))
			content = requests.get(url, headers = headers, data = data, timeout = 30).text
			#json转换
			total = json.loads(content)['paging']['totals']
			while total > curnum:
				sleep(random.uniform(0.5,1))
				content = requests.get(url,headers = headers,data = data,timeout = 30).text.encode('utf-8').decode('utf-8')
				curnum += 30
				data['offset'] = curnum
				jsondatas = json.loads(content)['data']
				for userdata in jsondatas:
					try:
						if self.allurls.has_key(userdata['url_token']) != True:
							print u'抓取第' + str(self.datanum) + u'个用户信息'
							self.allurls[userdata['url_token']] = False
							self.datanum = self.datanum + 1
							sql = "INSERT INTO zhihuuser (name,answer, follow, urltoken, headline, headurl) VALUES ('" + userdata['name'] + "', " + str(userdata['answer_count']) + ", " + str(userdata['follower_count']) + ", '" + userdata['url_token'] + "', '" + userdata['headline'] + "', '" + userdata['avatar_url'] + "')"
							self.cur.execute(sql)
							self.conn.commit()
					except Exception, e:
						print 'str(e):\t', str(e)
						pass

			for url in self.allurls:
				try:
					if threading.activeCount() < 3:
						if self.allurls[url] != True:
							self.allurls[url] = True
							threading.Thread(target = self.main, args = (url,), name = 'thread-' + str(self.datanum)).start()	
					else:
						break
				except:
					print u'错误'
					pass
		except Exception, e:
			print str(e)

if __name__ == '__main__':
	zhihuuser = Zhihuuser()
	zhihuuser.getusers()
