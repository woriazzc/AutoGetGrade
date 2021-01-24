# -*-coding:utf-8-*-
from user_login import *
from aline import aligns
from send_gmail import send_gmail
import os

os.chdir(os.path.dirname(__file__))

f = open("cur_g.txt", "a")
f.close()
with open("cur_g.txt", "r") as f:
    cur_grade = f.read()
Login()
nw_grade = getGrade()
if nw_grade != cur_grade:
    print("New Grade !!")
    cur_grade = nw_grade
    print("Send Email...")
    send_gmail(cur_grade)
    with open("cur_g.txt", "w") as f:
        f.write(cur_grade)
else:
    print("Nothing new.")