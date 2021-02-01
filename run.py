from jinja2 import FileSystemLoader, Environment
import os
from email.utils import formataddr
from email.header import Header
from email.mime.text import MIMEText
from lib import db
from lib import config
import requests
import schedule
import time
import json
import sys
import smtplib
import traceback
requests.packages.urllib3.disable_warnings()



class JOBRUN:
    def __init__(self) -> None:
        print(os.path.dirname(__file__)+"/.tmp")
        self.target_api = "https://api.github.com/repos/chaitin/xray"
        self.target_dir = "pocs"
        tmpPath = os.path.dirname(__file__)+"/data/.tmp"
        if os.path.exists(tmpPath):
            self.commitHistory = open(tmpPath).read()
        else:
            self.commitHistory = ""

    def sendEmail(self, pocs):
        path = '{}/templates/'.format(os.path.dirname(os.path.abspath(__file__)))
        loader = FileSystemLoader(path)
        env = Environment(loader=loader)
        template = env.get_template("tpl.html")
        data = template.render(pocs=pocs)
        message = MIMEText(str(data), 'HTML', 'utf-8')
        message['From'] = formataddr(["pocCheck", config.SMTP_SENDER])
        message['to'] = formataddr(["Reciver", config.SMTP_RECEIVER])
        subject = '【X-Ray】 POC更新'
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP_SSL(
                config.SMTP_SERVER, config.SMTP_SERVER_PORT)
            smtpObj.login(config.SMTP_SENDER, config.SMTP_SENDER_PASSWORD)
            smtpObj.sendmail(config.SMTP_SENDER, [
                             config.SMTP_RECEIVER], message.as_string())
            smtpObj.quit()
            print("[+] 邮件发送成功")
        except smtplib.SMTPException:
            traceback.print_exc()
            print("[-] Error: 无法发送邮件")

    def commitUpdate(self, newSHA):
        print("[+] 更新本地commit时间")
        f = open(sys.path[0]+"/data/.tmp", "w")
        f.write(newSHA)
        f.close()

    def compare(self):
        dbHandle = db.db()
        target = "{}/contents/{}".format(self.target_api, self.target_dir)
        updatePOCS = []
        try:
            r = requests.get(target, verify=False)
            pocs = json.loads(r.text)
            print("共{}条poc".format(len(pocs)))
            for poc in pocs:
                if not dbHandle.get(poc):
                    dbHandle.insert(poc)
                    updatePOCS.append(poc)
            if updatePOCS:
                self.sendEmail(updatePOCS)
                dbHandle.commit()
        except KeyError:
            traceback.print_exc()
        except:
            traceback.print_exc()

    def run(self):
        try:
            target_commit = self.target_api+"/commits"
            print("[+] 检测时间：{}".format(time.asctime(time.localtime(time.time()))))
            r = requests.get(target_commit, verify=False)
            newSHA = json.loads(r.text)[0].get("sha")
            if newSHA != self.commitHistory:
                print("[+] 发现新commit!")
                self.compare()
                self.commitUpdate(newSHA)
        except KeyError:
            traceback.print_exc()
        except:
            traceback.print_exc()

def job():
    JOBRUN().run()

if __name__ == "__main__":
    schedule.every().hour.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

