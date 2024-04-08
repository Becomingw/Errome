import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
from functools import wraps
import traceback


class Errome:
    def __init__(self,sender_email, password,recever):
        self.sender_email = sender_email
        self.sender_name = "程序运行情况"
        self.password = password
        self.recever = recever
        self.start_time = datetime.datetime.now()

    def set_start(self):
        self.start_time = datetime.datetime.now()

    def send_email(self, statu):
        
        message = MIMEMultipart("alternative")
        
        message["From"] = f"{self.sender_name}"
        message["To"] = self.recever
        current_time = datetime.datetime.now()
        time_cost = current_time - self.start_time
        if statu == "ok":
            message["Subject"] = "运行完成"
            with open("ok.html", 'r', encoding='utf-8') as file:
                html_content = file.read()
            html_content = html_content.replace(f"NowTime", current_time.strftime("%Y-%m-%d %H:%M:%S"))
            html_content = html_content.replace(f"Timeuse", str(time_cost.seconds)+"秒")

            part = MIMEText(html_content, "html")
            message.attach(part)
        else:
            message["Subject"] = "运行错误"
            with open("erro.html", 'r', encoding='utf-8') as file:
                html_content = file.read()
            html_content = html_content.replace(f"NowTime", current_time.strftime("%Y-%m-%d %H:%M:%S"))
            html_content = html_content.replace(f"Timeuse", str(time_cost.seconds)+"秒")
            html_content = html_content.replace(f"erro_code", statu)
            part = MIMEText(html_content, "html")
            message.attach(part)

        try:
            with smtplib.SMTP_SSL('smtp.163.com', 465) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.recever, message.as_string())
                print("Email sent")
        except :
            print("Email sent erro")
    def notify(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            self.start_time = datetime.datetime.now()
            try:
                result = func(*args, **kwargs)
                self.send_email("ok")
                return result
            except Exception as e:
                error_message = traceback.format_exc()
                self.send_email("error", error_message)
                raise
        return wrapped