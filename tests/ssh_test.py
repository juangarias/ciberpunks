import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.104', username='juan', password='juan')
sftpClient = client.open_sftp()
ret = sftpClient.put('/home/juan/instalacion_ciberpunks/window_input.log', '/Users/juan/faces/news/w.log')

print ret

client.close()
