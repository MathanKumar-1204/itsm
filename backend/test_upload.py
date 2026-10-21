import urllib.request
import uuid

boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
file_content = b'VPN Setup Guide for Enterprise Employees.\nStep 1: Download Cisco AnyConnect.\nStep 2: Enter portal gateway address vpn.enterprise.com.\nStep 3: Authenticate using company Okta SSO credentials and approve Duo push.\nStep 4: Once connected, status indicator turns green.\nFor issues, contact helpdesk@enterprise.com.'

body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="title"\r\n\r\n'
    f'Enterprise VPN Configuration Runbook\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="category"\r\n\r\n'
    f'Network\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="vpn_runbook.txt"\r\n'
    f'Content-Type: text/plain\r\n\r\n'
).encode('utf-8') + file_content + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    'https://itsm-lqs3.vercel.app/api/knowledge/documents',
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': 'Bearer dev-token-admin',
        'X-Dev-Mode': 'true',
        'X-Dev-User-Role': 'admin'
    }
)

try:
    with urllib.request.urlopen(req) as res:
        print('STATUS:', res.status)
        print('RESPONSE:', res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode('utf-8'))
except Exception as ex:
    print('Exception:', ex)
