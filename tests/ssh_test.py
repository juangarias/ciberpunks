import paramiko

try:
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect('192.168.1.197', username='juan', password='juancito')
  sftpClient = client.open_sftp()
  ret = sftpClient.put('/home/juan/instalacion_ciberpunks/window_input.log', '/Users/juan/faces/news/w.log')

  print ret
except Exception as e:
  print type(e).__name__

client.close()
