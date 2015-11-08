import logging
import paramiko


class MultipleSSHClient(object):

    """docstring for MultipleSSHClient"""
    def __init__(self, sshServerIP, sshUser, sshPassword):
        super(MultipleSSHClient, self).__init__()

        self.sshServersIPs = sshServerIP.split(',')
        self.sshUsers = sshUser.split(',')
        self.sshPasswords = sshPassword.split(',')

        if len(self.sshServersIPs) != len(self.sshUsers) or len(self.sshServersIPs) != len(self.sshPasswords):
            raise ValueError('Incorrect number of ssh hosts, users and passwords.')

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
        i = 0
        logging.debug('Trying to send file tp {0} servers.'.format(len(self.sshServersIPs)))
        for sshHost, sshUser, sshPassword in zip(self.sshServersIPs, self.sshUsers, self.sshPasswords):
            sshClient = self.openSSH(sshHost, sshUser, sshPassword)
            logging.debug('Trying to open SFTP client for server {0}...'.format(i))
            sftpClient = sshClient.open_sftp()
            logging.debug('Connect to SSH and SFTP server OK.')

            remotepath = filename
            logging.debug('Trying to put remote file to {0}'.format(remotepath))
            ret = sftpClient.put(localpath, remotepath)
            logging.debug('File transferred to server in {0} with result {1}.'.format(remotepath, ret))

            logging.debug('Trying to close sFTP and SSH connections...')
            self.tryClose(sftpClient)
            self.tryClose(sshClient)
            logging.debug('Close sFTP and SSH connections OK!')
            i += 1

    def close(self):
        pass

    def tryClose(self, client):
        try:
            client.close()
        except:
            pass

