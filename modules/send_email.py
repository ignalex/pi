import os, smtplib
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Utils import COMMASPACE, formatdate 
from email import encoders

def sendMail(to, from_credentials, subject, text, files): 
    try: 
        assert type(to)==list 
        assert type(files)==list 
        
        from_addr = from_credentials[0]
                
        connection = smtplib.SMTP_SSL('smtp.gmail.com') 
        connection.login(from_credentials[1],from_credentials[2])    
       
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = COMMASPACE.join(to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(text))
        
        for file_ in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(file_,"rb").read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                           % os.path.basename(file_))
            msg.attach(part)
           
        connection.sendmail(from_addr, msg['To'] , msg.as_string() )      
        connection.close()
        return 'sent'
    except Exception, exc:
        return "ERROR SENDING E-MAIL: "+ str(exc)

def MyIP():
    from requests import get
    return get('https://api.ipify.org').text

if __name__ == '__main__': 
    import sys 
    sys.path.append('/home/pi/git/pi/') #for crontab 
    from modules.common import CONFIGURATION, LOGGER, LastLine
    p = CONFIGURATION()
    if len(sys.argv)> 1: 
        "syntax : python send_email.py ip {to} {from} {login} {pass} "
        logger = LOGGER('send_ip')
        try: 
            if sys.argv[1] == 'ip' :
                _ip, _to, _from_addr, _from_login, _from_pass = sys.argv[1:]
                IP = MyIP()
                if LastLine('/home/pi/LOG/send_ip').find(IP) == -1: # updated 
                    reply = sendMail([_to], [_from_addr, _from_login, _from_pass], 'IP', IP ,[]) +  'IP changed' 
                else: 
                    reply = 'IP same '
            logger.info('OK, IP =' + IP + ' ' + reply)
        except: 
            logger.error('NOT GOOD. IP =' + IP + ' ' + reply)