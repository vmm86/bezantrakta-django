import dns.resolver
import re
import smtplib


def check_email(to_email):
    # Address used for SMTP MAIL FROM command
    from_email = 'office@rterm.ru'

    # Simple Regex for syntax checking
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'

    # Syntax check
    match = re.match(regex, to_email)
    if match is None:
        print('Bad Syntax')
        raise ValueError('Bad Syntax')

    # Get domain for DNS lookup
    domain = to_email.split('@')[1]
    print('Domain:', domain)

    # MX record lookup
    records = dns.resolver.query(domain, 'MX')
    mx_record = str(records[0].exchange)

    # SMTP lib setup (use debug level for full output)
    server = smtplib.SMTP()
    server.set_debuglevel(0)

    # SMTP Conversation
    try:
        server.connect(mx_record)
        server.helo(server.local_hostname)  # server.local_hostname (Get local server hostname)
        server.mail(from_email)
        code, message = server.rcpt(to_email)
        server.quit()
    except ConnectionRefusedError as e:
        print('ConnectionRefusedError: ', e)
        print('return False')
        return False

    print('code: ', code)
    print('message: ', message)

    # Assume SMTP response 250 is success
    if code == 250:
        print('return True')
    else:
        print('return False')
    return True if code == 250 else False

check_email('michail-vasilyev@yandex.ru')
# check_email('a.dubacova@gmai.com')
# check_email('a.dubacova@gmail.com')
