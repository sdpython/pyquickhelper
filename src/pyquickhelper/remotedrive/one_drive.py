"""
@file
@brief Implements class OneDrive

.. versionadded:: 1.3
"""

from .cloud_drive import CloudDrive


class OneDrive(CloudDrive):
    """
    Implements CloudDrive API for `OneDrive <https://onedrive.live.com/>`_.
    It relies on `onedrive-sdk-python <https://github.com/OneDrive/onedrive-sdk-python>`_

    credentials must be obtained by creating an application:
    `Registering your app for OneDrive API <https://dev.onedrive.com/app-registration.htm#register-your-app-for-onedrive>`_
    """

    def __init__(self, user, pwd, drive="me", rid="root", fLOG=None):
        """
        constructor

        @param      user        user name
        @param      pwd         password
        @param      drive       drive name
        @param      rid         root id
        @param      fLOG        logging function
        """
        CloudDrive.__init__(self, user, pwd, fLOG=fLOG)
        import onedrivesdk
        self.onedrivesdk = onedrivesdk
        from onedrivesdk.helpers import GetAuthCodeServer
        self.GetAuthCodeServer = GetAuthCodeServer
        self._client = onedrivesdk.get_default_client(client_id=user,
                                                      scopes=['wl.signin',
                                                              'wl.offline_access',
                                                              'onedrive.readwrite'])
        self._redirect_uri = "http://localhost/"
        self._drive = drive
        self._rid = rid

    def connect(self):
        """
        connect
        """
        self.fLOG("connect begin")
        self._auth_url = self._client.auth_provider.get_auth_url(
            self._redirect_uri)
        self.fLOG("connect 1", self._auth_url)
        self._code = self.GetAuthCodeServer.get_auth_code(
            self._auth_url, self._redirect_uri)
        self.fLOG("connect 2", self._code)
        self._client.auth_provider.authenticate(
            self._code, self._redirect_uri, self._pwd)
        self.fLOG("connect 3")
        self._drive = self._client.item(drive=self._drive, id=self.rid)
        self._folders[""] = self._drive
        self.fLOG("connect end")

    def close(self):
        """
        close the connection
        """
        self._auth_url = None
        self._code = None
        self._drive = None
        self._folders = None

    def _get_folder(self, remote_path):
        """
        get a folder object base on the remote_path,
        we assume *remote_path* is always a filename

        @param  remote_path     remote_path
        @return                 folder object, filename
        """
        path = remote_path.replace("\\", "/").split("/")
        folder = "/".join(path[:-1])
        filename = path[-1]
        if folder in self._folders:
            return self._folders[folder], filename
        scur = ""
        cur = self._folders[""]
        for p in path:
            if not len(scur).endswith("/"):
                scur += "/"
            scur += p
            if scur in self._folders:
                cur = self._folders[scur]
            else:
                f = cur.children.get()
                res = None
                for ind in f:
                    if ind.name == p:
                        res = ind
                        break
                if cur is None:
                    # we create it
                    f = self.onedrivesdk.Folder()
                    i = self.onedrivesdk.Item()
                    i.name = p
                    i.folder = f
                    cur = cur.children.add(i)
                else:
                    cur = res
        return cur, filename

    def upload_data(self, remote_path, data):
        """
        upload binary data

        @param      remote_path     path on the remote drive
        @param      data            bytes
        @return                     boolean
        """
        fold, filename = self._get_folder(remote_path)
        fold.children[filename].upload(data)
        return True

    def download_data(self, remote_path):
        """
        download binary data

        @param      remote_path     path on the remote drive
        @return                     data (bytes)
        """
        fold, filename = self._get_folder(remote_path)
        data = fold.children[filename].download()
        return data
