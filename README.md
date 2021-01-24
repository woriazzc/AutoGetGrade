# AutoGetGrade

通过python访问ECNU公共数据库，自动化查成绩，或定时查成绩并在有新成绩时发送邮件通知。

### 安装依赖

python 3.6及以上。

需要依赖库：pillow，pytesseract，PyExecJS，lxml，requests，getpass，bs4

### 使用方法

1. 在 user_login.py 中的 Login() 函数中填入 username 和 password。

2. 在 send_gmail 中填入mail_host, mail_sender, mail_license, mail_receiver。
3. 在 send_gmail 中的 send_gmail() 函数中的 mm["From"]=“” 中填入 “your nickname”。
4. 在cmd中移动到当前目录，运行 python main.py

### 扩展功能

如果有服务器的话，可以加个定时任务，定时执行main.py。

### 可增加功能

通过传参指定用户名，密码，邮箱。

部署到网页上，用户在网页端输入用户名，密码，邮箱，服务端为其增加定时任务。

以上产生安全性问题。

