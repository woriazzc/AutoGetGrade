# -*-coding:utf-8-*-
from PIL import Image  # 手动输入验证码
import pytesseract  # 自动识别验证码
from lxml import etree
import sys
import requests
import getpass
import execjs  # 用于加密
import re
from aline import aligns
from bs4 import BeautifulSoup

LOGIN_URL = 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fportal.ecnu.edu.cn%2Fneusoftcas.jsp'
CODE_URL = "https://portal1.ecnu.edu.cn/cas/code"
TARGET_URL = "http://portal.ecnu.edu.cn/neusoftcas.jsp"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
DES_URL = "https://portal1.ecnu.edu.cn/cas/comm/js/des.js"
GRADE_URL = "http://applicationnewjw.ecnu.edu.cn/eams/teach/grade/course/person!search.action?semesterId=897"

headers = {
	'User-Agent': UA,
	'Referer':LOGIN_URL
}
# 记录登录信息的 session
s = requests.session()

def GetRSA(username, password, lt):
	# 获取 des.js 里的内容
	jsstr = requests.get(DES_URL).text
	desJS = execjs.compile(jsstr)
	# 调用 strEnc 函数实现 rsa 加密
	try:
		rsa = desJS.call('strEnc', username + password + lt, '1', '2', '3')
	except:
		print('加密错误。')

	return rsa

def GetCode():
	# 发送一次新的 get 请求并获取验证码
	print('正在获取验证码...')
	imgraw = s.get(CODE_URL, headers = headers)
	with open(sys.path[0] + '/temp.jpg', 'wb+') as f:
		f.write(imgraw.content)

	print('正在识别验证码...')
	img = Image.open(sys.path[0] + '/temp.jpg')
	captacha = pytesseract.image_to_string(img)
	code = ''
	for c in captacha:
		if(c.isdigit()):
			code = code + c
	print('识别结果： {}'.format(code))
	return code


def ECNULogin(username='', password='', ifEnterPassword=False):
	"""
	返回值：
	0 - 成功登陆
	1 - 验证码错误
	2 - 密码错误
	3 - 未知错误
	"""
	if (ifEnterPassword == True):
		username = input('请输入你的公共数据用户名（学号）：')
		password = getpass.getpass('请输入你的公共数据库密码（直接输入即可，已关闭输入回显）：')


	r = s.get(LOGIN_URL, headers=headers)

	elements = etree.HTML(r.content)

	js = elements.xpath('//*[@id="account_template"]//text()')[0]
	lt = re.search(r'id="lt" name="lt" value="(\S+)"', js).group(1)
	execu = re.search(r'name="execution" value="(\S+)"', js).group(1)

	code = GetCode()
	# 用户名和密码经过了 RSA 加密。
	postData = {
		'code': code,
		'rsa': GetRSA(username, password, lt),
		'ul': len(username),
		'pl': len(password),
		'lt': lt,
		'execution': execu,
		'_eventId': 'submit'
	}
	print('正在尝试登录...')
	r = s.post(LOGIN_URL, data=postData, headers = headers)

	elements = etree.HTML(r.content)
	errors = elements.xpath('//*[@id="errormsg"]')

	r = s.get(TARGET_URL, headers = headers)
	elements = etree.HTML(r.content)

	if len(errors) == 0:
		realName = elements.xpath('//*[@id="portlet_content_P-1229b4e17f9-10004"]/tr/td[2]/table/tr/td/table/tr/td[2]/table[2]/tr[1]/td/div/strong/font/text()')[0]
		print('登录成功:', realName)
		return 0
	elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "验证码有误":
		return 1
	elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "用户名密码错误":
		return 2
	else:
		return 3


def Login():
	# username = input('请输入你的公共数据用户名（学号）：')
	# password = getpass.getpass('请输入你的公共数据库密码（直接输入即可，已关闭输入显示）：')
	username = "your username"
	password = "your password"
	feedback = ECNULogin(username, password, ifEnterPassword=False)
	t = 5
	while feedback != 0 and t > 0:
		t -= 1
		if feedback == 1:
			print('验证码识别错误，请重试。')
			feedback = ECNULogin(username, password, ifEnterPassword=False)
		elif feedback == 2:
			print('用户名或密码错误，请重试。')
			feedback = ECNULogin(ifEnterPassword=True)
		else:
			print('未知错误，输入 0 以重试，输入其他任何内容退出。')
			c = input()
			if (c == '0'):
				feedback = ECNULogin(ifEnterPassword=True)
			else:
				print('无法连接。')
	return feedback


def getGrade():
	r = s.get(GRADE_URL).content
	html = etree.HTML(r,parser=etree.HTMLParser(encoding='utf-8'))
	trs = html.xpath("//tr")
	grade = ""
	le = len(trs)
	for i in range(1, le):
		tr = trs[i]
		chs = tr.getchildren()
		for c in chs:
			cs = c.getchildren()
			txt = ""
			if len(cs) != 0:
				txt = cs[0].text.strip()
			else:
				txt = c.text.strip()
			grade += aligns(txt, 25)
		grade += "\n"
	return grade