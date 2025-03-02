import datetime
import os

# from pkg_resources import resource_filename
import importlib.resources as pkg_resources
import smtplib
import sys
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps


class Errome:
    _instance = None

    def __init__(self, sender_email=None, password=None, recever=None, smtp_server=None, message=None):
        if Errome._instance is None:
            Errome._instance = self
            
        # 从环境变量获取值，如果参数未提供
        self.sender_email = sender_email or os.environ.get('ERROME_SENDER_EMAIL')
        self.password = password or os.environ.get('ERROME_PASSWORD')
        self.recever = recever or os.environ.get('ERROME_RECEIVER')
        
        # 验证必要的值是否存在
        if not all([self.sender_email, self.password, self.recever]):
            raise ValueError(
                "Please provide sender_email, password, and recever either as parameters "
                "or set them as environment variables (ERROME_SENDER_EMAIL, ERROME_PASSWORD, ERROME_RECEIVER)"
            )
            
        self.sender_name = "Errome程序运行情况提示"
        self.start_time = datetime.datetime.now()
        self.platform = sys.platform
        self.smtp_server = (
            f"smtp.{self.sender_email.split('@')[1]}"
            if smtp_server is None
            else smtp_server
        )
        self.file_header = "templates\\" if "windows" in self.platform else "templates/"
        self.define_message = message

    def set_start(self):
        self.start_time = datetime.datetime.now()

    def ini_start_sent(self, project_name=None, define_message=None):
        self.set_start()
        if project_name is None:
            project_name = f"{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.define_message = define_message
        if define_message is None:
            self.define_message = "无"
        message = MIMEMultipart("alternative")

        message["From"] = f"{self.sender_name}"
        message["To"] = self.recever
        message["Subject"] = f"{project_name}在Errome的监护下开始运行"
        
        # 获取模板文件的绝对路径
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        with open(os.path.join(template_dir, 'start.html'), 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        html_content = html_content.replace(
            "NowTime", self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        html_content = html_content.replace("project_name", project_name)
        html_content = html_content.replace("Message", define_message)

        part = MIMEText(html_content, "html")
        message.attach(part)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, 465) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.recever, message.as_string())
                # print("Initial email sent")
        except:
            print("Initial email sending failed")

    def send_email(self, statu, project_name=None, define_message=None):
        message = MIMEMultipart("alternative")

        message["From"] = f"{self.sender_name}"
        message["To"] = self.recever
        current_time = datetime.datetime.now()
        time_cost = current_time - self.start_time
        if project_name is None:
            project_name = f"{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        if define_message is None:
            define_message = "无"
        if statu == "ok":
            message["Subject"] = f"{project_name}_运行完成"
            # 获取模板文件的绝对路径
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
            with open(os.path.join(template_dir, 'ok.html'), 'r', encoding='utf-8') as file:
                html_content = file.read()
            total_seconds = int(time_cost.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes}分钟{seconds}秒"
            html_content = html_content.replace(
                "NowTime", current_time.strftime("%Y-%m-%d %H:%M:%S")
            )
            html_content = html_content.replace("Timeuse", time_str)
            html_content = html_content.replace("project_name", project_name)

            html_content = html_content.replace("Message", define_message)
            part = MIMEText(html_content, "html")
            message.attach(part)
        else:
            message["Subject"] = f"{project_name}_运行错误"
            # 获取模板文件的绝对路径
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
            with open(os.path.join(template_dir, 'erro.html'), 'r', encoding='utf-8') as file:
                html_content = file.read()
            total_seconds = int(time_cost.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes}分钟{seconds}秒"
            html_content = html_content.replace("project_name", project_name)
            html_content = html_content.replace(
                "NowTime", current_time.strftime("%Y-%m-%d %H:%M:%S")
            )
            html_content = html_content.replace("Timeuse", time_str)
            html_content = html_content.replace("erro_code", statu)
            html_content = html_content.replace("Message", define_message)
            part = MIMEText(html_content, "html")
            message.attach(part)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, 465) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.recever, message.as_string())
                # print("Email sent")
        except:
            print("Email sent erro")

    # def notify(self, func):
    #     @wraps(func)
    #     def wrapped(*args, **kwargs):
    #         project_name = func.__name__
    #         self.ini_start_sent(project_name)
    #         try:
    #             result = func(*args, **kwargs)
    #             self.send_email("ok",project_name=project_name)
    #             return result
    #         except Exception as e:
    #             error_message = traceback.format_exc()
    #             self.send_email(error_message,project_name=project_name)
    #             raise
    #     return wrapped

    @classmethod
    def notify(
        cls,
        func=None,
        sender_email=None,
        password=None,
        recever=None,
        smtp_server=None,
        message=None,
    ):
        if func is None:
            return lambda f: cls.notify(f, sender_email, password, recever, smtp_server)

        @wraps(func)
        def wrapped(*args, **kwargs):
            if cls._instance is None:
                if issubclass(cls, Errome) and cls is not Errome:
                    cls._instance = cls(recever)
                else:
                    if sender_email is None or password is None or recever is None:
                        raise ValueError(
                            "Please provide sender_email, password, and recever for Errome initialization"
                        )
                    cls._instance = cls(sender_email, password, recever, smtp_server)

            project_name = func.__name__
            cls._instance.ini_start_sent(project_name, define_message=message)
            try:
                result = func(*args, **kwargs)
                cls._instance.send_email(
                    "ok", project_name=project_name, define_message=message
                )
                return result
            except Exception as e:
                error_message = traceback.format_exc()
                cls._instance.send_email(
                    error_message, project_name=project_name, define_message=message
                )
                raise

        return wrapped


class ERM(Errome):
    @classmethod
    def notify(cls, func=None, recever=None, message=None):
        if func is None:
            return lambda f: cls.notify(f, recever, message=message)
        return super().notify(
            func,
            sender_email="Errome@scosine.org",
            password="pbFPloo6P34CbtHo",
            recever=recever,
            smtp_server="smtp.feishu.cn",
            message=message,
        )

    def __init__(self, recever=None, message=None):
        # 如果没有提供recever，从环境变量获取
        recever = recever or os.environ.get('ERROME_RECEIVER')
        super().__init__(
            sender_email="Errome@scosine.org",
            password="pbFPloo6P34CbtHo",
            recever=recever,
            smtp_server="smtp.feishu.cn",
            message=message
        )


if __name__ == "__main__":
    # 邮件发送者和接收者
    sender_email = "XXXXXXXXXXX@163.com"  # 替换为你的163邮箱地址
    receiver_email = "becomingw@qq.com"  # 接收者的邮箱地址
    password = "*********"  # 你的163邮箱密码
    # Email = Errome(sender_email=sender_email, recever=receiver_email, password=password)
    Email = ERM(recever=receiver_email)

    @ERM.notify(recever=receiver_email, message="测试邮件")
    def test_function():
        i = 10 / 0
        # timesleep(10)
        # print("apple")

    test_function()
