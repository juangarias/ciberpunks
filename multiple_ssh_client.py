import logging
import paramiko


class MultipleSSHClient(object):

    """docstring for MultipleSSHClient"""
    def __init__(self, sshServerIP, sshUser, sshPassword):
        super(MultipleSSHClient, self).__init__()

        self.sshServersIPs = sshServerIP.split(',')
        self.sshUsers = sshUser.split(',')
        self.sshPasswords = sshPassword.split(',')
        self.sshClients = []

        for server, user, pwd in zip(self.sshServersIPs, self.sshUsers, self.sshPasswords):
            self.sshClients.append(self.openSSH(server, user, pwd))

    def openSSH(self, sshHost, sshUser, sshPassword):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logging.debug('Trying to connect to SSH server {0}...'.format(sshHost))
            sshClient.connect(sshHost, username=sshUser, password=sshPassword)
            logging.debug('Connect to SSH server OK.')

            return sshClient
        except:
            logging.error('Could not connect to server.')
            raise paramiko.SSHException('Could not connect to server')

    def send(self, filename, localpath, remoteFolder):
        for sshClient in self.sshClients:
            logging.debug('Trying to open SFTP client...')
            sftpClient = sshClient.open_sftp()
            logging.debug('Connect to SSH and SFTP server OK.')

            remotepath = remoteFolder + '/' + filename
            logging.debug('Trying to put remote file to {0}'.format(remotepath))
            ret = sftpClient.put(localpath, remotepath)
            logging.debug('File transferred to server in {0} with result {1}.'.format(remotepath, ret))

            self.tryClose(sftpClient)

    def close(self):
        for client in self.sshClients:
            self.tryClose(client)

    def tryClose(self, client):
        try:
            client.close()
        except:
            pass
