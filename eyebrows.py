# -*- coding: utf-8 -*-
# General socket/connection stuff
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse
import urllib.request
# SSL/authentication
from socketserver import BaseServer
import socket
import ssl
import base64
# Misc
import os
import shutil
import sys
import datetime
import time
<<<<<<< HEAD
import json
import math
# Tweaked / project specific
if os.path.dirname(__file__) != "":
    os.chdir(os.path.dirname(__file__))
sys.path.insert(0, 'lib')
sys.path.insert(0, os.path.join('lib', 'zipstream'))
=======
this_file = __file__
def rel_dir(*what):
    x = os.path.dirname(os.path.abspath(this_file))
    for i, w in enumerate(what):
        x = os.path.join(x, w)
    return os.path.normpath(x)

sys.path.insert(0, rel_dir('lib'))
>>>>>>> refs/remotes/origin/master
import cgi_tweaked as cgi
import mako  # for the version
from mako.template import Template
from mako.lookup import TemplateLookup
<<<<<<< HEAD
import zipstream    # for zip file generation
=======
sys.path.insert(0, rel_dir('lib', 'zipstream'))
import json
import math
# Used for zip file generation
import zipstream
>>>>>>> refs/remotes/origin/master
# Project files
from icontypes import fileIcons
from utils import *
# Config
import threading
import atexit

class NotAllowedException(BaseException):
    '''whatever'''

def base_dir(*what):
    x = os.path.abspath(config.baseFolder)
    for i, w in enumerate(what):
        print("what", w)
        x = os.path.join(x, w)
    x = os.path.normpath(x)
    if not x.startswith(os.path.abspath(config.baseFolder)):
        print(x, "does not start with", os.path.abspath(config.baseFolder))
        x = ""
        for i, w in enumerate(what):
            x = os.path.join(x, w)
        raise NotAllowedException(x)
    return x

# Class to hold configuration
class Config:
    baseFolder = os.path.expanduser("~")
    port = 8080
    hideBarsDelay = 3000
    protocol = "HTTP/1.0"
    useSSL = False
    username = "admin"
    password = "admin"
    ignoreHidden = False
    strictIgnoreHidden = False
    useDots = False
    sortFoldersFirst = True
    uploadEnabled = True
    def saveToFile(self):
        pass
    def loadFromFile(self):
        import config as userConfig
        try:
            self.baseFolder = userConfig.baseFolder
            if (os.name == 'nt' and self.baseFolder.endswith('\\') and self.baseFolder.length()>3) or (os.name != 'nt' and self.baseFolder.endswith('/')):
                self.baseFolder = self.baseFolder[:-1]
        except:
            pass
        try:
            self.port = userConfig.port
        except:
            pass
        try:
            self.hideBarsDelay = userConfig.hideBarsDelay
        except NameError:
            pass
        try:
            self.protocol = userConfig.protocol
        except:
            pass
        try:
            self.useSSL = userConfig.useSSL
        except:
            pass
        try:
            self.username = userConfig.username
        except:
            pass
        try:
            self.password = userConfig.password
        except:
            pass
        try:
            self.ignoreHidden = userConfig.ignoreHidden
        except:
            pass
        try:
            self.strictIgnoreHidden = userConfig.strictIgnoreHidden
        except:
            pass
        try:
            self.useDots = userConfig.useDots
        except:
            pass
        try:
            self.sortFoldersFirst = userConfig.sortFoldersFirst
        except:
            pass
        try:
            self.uploadEnabled = userConfig.uploadEnabled
        except:
            pass

# Global Variables
server = None
config = Config()
config.loadFromFile()
# Variables that are automatically set. DO NOT TOUCH
__version__ = 1.0
depVersions = {"python": ".".join(str(x) for x in sys.version_info[0:3]),
               "mako": mako.__version__,
               "zipstream": zipstream.__version__,
               "fineuploader": "4.2.1",
               "jquery": "1.10.2",
               "bootstrap": "3.0.3",
               "fontawesome": "4.0.3",
               "swipebox": "1.4.4"}

if os.name == 'nt':
    try:
        import win32api
        import win32con
        depVersions["pywin32"] = win32api.GetFileVersionInfo(win32api.__file__, "\\")['FileVersionLS'] >> 16
    except ImportError:
        config.ignoreHidden = False
        config.strictIgnoreHidden = False

maintemplate = Template(filename=rel_dir('views/main.html'), lookup=TemplateLookup(directories=[rel_dir('views/')]))
uptemplate = Template(filename=rel_dir('views/upload.html'), lookup=TemplateLookup(directories=[rel_dir('views/')]))
errortemplate = Template(filename=rel_dir('views/error.html'), lookup=TemplateLookup(directories=[rel_dir('views/')]))
infotemplate = Template(filename=rel_dir('views/info.html'), lookup=TemplateLookup(directories=[rel_dir('views/')]))
chunk_dir = "chunks"


### Main class that handles everything ###
class MyHandler(SimpleHTTPRequestHandler):
    def __init__(self, req, client_addr, server):
        SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)
<<<<<<< HEAD

    def do_OPTIONS(self):
        self.send_response(200)
        if config.protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        self.end_headers()

    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        SimpleHTTPRequestHandler.end_headers(self)


=======
        
>>>>>>> refs/remotes/origin/master
    def send_401(self):
        print("Sending 401")
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Log in\"')
        if config.protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        SimpleHTTPRequestHandler.end_headers(self)

    ## Handle Get requests
    def do_GET(self):
        try:
            theArg = urllib.parse.unquote(self.path.split("?")[0])[1:]
            if theArg == "~":
                return self.info()
            # paths that start with /~ refer to the directory
            if theArg.startswith("~/css") or theArg.startswith('~/js') or theArg.startswith('~/img') or theArg.startswith('~/fonts'):
                return self.getResource(theArg[2:])
            if authstring and self.headers.get('Authorization') != authstring:
                print(authstring + " vs " + ("<None>" if self.headers.get('Authorization') is None else self.headers.get('Authorization')))
                return self.send_401() # authorization required
                

            print("theArg", theArg)
            parameters = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            pathVar = base_dir(theArg)
            # Handle the file or folder
            if os.path.isdir(pathVar):
                if "u" in parameters and parameters["u"]:
                    self.showUpload(theArg)
                elif self.headers.get("Accept") == "application/json" or self.headers.get("Content-Type") == "application/json":
                    self.doJSON(theArg)
                else:
                    self.doFolder(theArg)
            if os.path.isfile(pathVar):
                self.downloadFile(theArg, parameters)
        except NotAllowedException as exception:
            self.notAllowed(str(exception))

    ## Serve a resource that lives in the same folder as Eyebrows, such as CSS or JS
    def getResource(self, relPath):
        print("Resourcing: " + relPath)
        fullPath = rel_dir(relPath)
        if not fullPath.startswith(rel_dir()):
            print("Not Allowed: " + fullPath)
            return self.notAllowed(relPath)
        if not os.path.isfile(fullPath):
            return self.notFound(relPath)
        
        f = open(fullPath, 'rb')
        self.send_response(200)

        dat = f.read()
        self.send_header("Content-length", len(dat))
        if config.protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        self.end_headers()
        self.wfile.write(dat)
        self.wfile.flush()
        f.close()

    ## Download or view a file when requested from a GET
    def downloadFile(self, relPath, parameters):
        print("Downloading: " + relPath)
        fullPath = base_dir(relPath)
        if not os.path.isfile(fullPath):
            return self.notFound(relpath)
        
        if "i" in parameters and parameters["i"]:
            SimpleHTTPRequestHandler.do_GET(self)
            return

        derp, ext = os.path.splitext(relPath)
        ext = ext[1:].lower()
        f = open(fullPath, 'rb')
        self.send_response(200)
        if ext == "html" or ext == "htm":
            self.send_header('Content-type', 'text/html;charset=utf-8')
        dat = f.read()
        self.send_header("Content-length", len(dat))
        if config.protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        self.end_headers()
        self.wfile.write(dat)
        self.wfile.flush()
        f.close()

    ## Send the data back as JSON
    def doJSON(self, subfolder):
        folder = base_dir(relPath)
        if not os.path.isdir(folder):
            return self.notFound(subfolder)
        if os.path.islink(folder):
            print("Found a symlink")
            folder = os.path.realpath(folder)
        page_title = os.path.basename(subfolder)
        folderList = sorted(listdir_dirs(folder, config.strictIgnoreHidden or config.ignoreHidden), key=lambda s: s.lower())
        fileList = sorted(listdir_files(folder, config.strictIgnoreHidden or config.ignoreHidden), key=lambda s: s.lower())
        print("json: " + json.dumps(folderList))
        
        r = []
        
        for f in folderList:
            try:
                os.path.getmtime(os.path.join(folder, f))
                r.append({"name": f,
                          "size": 0,
                          "icon": "folder",
                          "mtime": math.floor(os.path.getmtime(os.path.join(folder, f))),
                          "atime": math.floor(os.path.getatime(os.path.join(folder, f))),
                          "ctime": math.floor(os.path.getmtime(os.path.join(folder, f)))
                          })
            except BaseException:
                print("Exception on: " + f)
            
        for f in fileList:
            try:
                os.path.getmtime(os.path.join(folder, f))
                derp, ext = os.path.splitext(f)
                r.append({"name": f,
                          "size": os.path.getsize(os.path.join(folder, f)),
                          "icon": fileIcons[ext[1:].lower()] if (ext[1:].lower() in fileIcons) else "file-o", 
                          "mtime": math.floor(os.path.getmtime(os.path.join(folder, f))),
                          "atime": math.floor(os.path.getatime(os.path.join(folder, f))),
                          "ctime": math.floor(os.path.getmtime(os.path.join(folder, f)))
                          })
            except BaseException:
                print("Exception on: " + f)
        
        r = json.dumps(r)
        self.send_response(200)
        self.send_header("Content-type", "application/json;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()

    ## Display a folder
    def doFolder(self, subfolder):
        folder = base_dir(subfolder)
        if not os.path.isdir(folder):
            return self.notFound(subfolder)
        if os.path.islink(folder):
            print("Found a symlink")
            folder = os.path.realpath(folder)

        up_level = os.path.dirname(subfolder) if subfolder else ""
        page_title = os.path.basename(subfolder)
        nav_folders = os.path.normpath(os.path.join(config.baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        itemList = sorted(listdir(folder, config.strictIgnoreHidden or config.ignoreHidden),
                          key=((lambda s: [-s[1], s[0].lower()]) if config.sortFoldersFirst else (lambda s: s[0].lower()))) 
        r = maintemplate.render(dep=depVersions,
                                subfolder=subfolder,
                                up_level=up_level,
                                page_title=page_title,
                                nav_folders=nav_folders,
                                itemList=itemList,
                                fileIcons=fileIcons,
                                config=config)
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()

    def foldersFirstCmp(itemA, itemB):
        if itemA[1] != itemB[1]:
            return itemA[1] - itemB[1]
        return itemA[0] - itemB[0]

    def notFoldersFirstCmp(item1, item2):
        return itemA[0] - itemB[0]
   

    ## Respond to POSTs; used for requesting zip files
    def do_POST(self):
        try:
            if authstring and self.headers.get('Authorization') != authstring:
                print(authstring + " vs " + ("<None>" if self.headers.get('Authorization') is None else self.headers.get('Authorization')))
                return self.send_401() # authorization required

            print("Posted: " + self.path)
            print(self.headers)
            if self.path == "/~":
                post_data = urllib.parse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
                print(post_data)
                self.downloadZip(post_data['subfolder'][0] if 'subfolder' in post_data else "", post_data['items'])
            else:
                self.uploadFile()
        except NotAllowedException as notAllowed:
            self.notAllowed(notAllowed)


    def uploadFile(self):
        if not config.uploadEnabled:
            self.notAllowed(self.path[1:])
            return

        def reject(reason, code):
            r = '{"error": "' + reason + '", "preventRetry": true}'
            self.send_response(code)
            self.send_header("Content-type", "text/plain;charset=utf-8")
            self.send_header("Content-length", len(r))
            self.end_headers()
            self.wfile.write(r.encode("utf-8"))
            self.wfile.flush()

        def accept():
            r = '{"success": true}'
            self.send_response(200)
            self.send_header("Content-type", "text/plain;charset=utf-8")
            self.send_header("Content-length", len(r))
            self.end_headers()
            self.wfile.write(r.encode("utf-8"))
            self.wfile.flush()

        print("Ok uploading file")
        subfolder = urllib.parse.unquote(self.path[1:])
<<<<<<< HEAD
        ctype = None
        if self.headers['Content-Type'] != None:
            ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
=======
        base_dir(subfolder)   ## Check for valid path
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
>>>>>>> refs/remotes/origin/master
        print("Parsed header")
        if ctype != 'multipart/form-data':
            url = None
            if ctype == "application/json":
                raw_data = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
                form = json.loads(raw_data)
                url = form['url']
            else: # assumes "application/x-www-form-urlencoded"
                raw_data = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
                print(raw_data)
                form = urllib.parse.parse_qs(raw_data)
                url = form['url'][0]
                print(form)
            if url is None:
                reject('No file or URL supplied', 400)
                return
            if 'filename' in form:
                filename = form['filename']
            else:
                filename = os.path.basename(urllib.parse.urlparse(url).path)
            dest = base_dir(subfolder, filename)
            if os.path.exists(dest):
                reject("File exists", 409)
                return
            print("Uploading " + url + " to " + dest)
            urllib.request.urlretrieve(url, dest)
        else:
            attrs = cgi.parse_multipart(self.rfile, pdict)  # qquuid, qqfilename, qqtotalfilesize, qqfile
            print("Parsed multipart")
            print(attrs['qqfilename'])
            chunked = False
            filename = attrs['qqfilename'][0].decode('utf-8')
            dest = base_dir(subfolder, subfolder, filename)
            if os.path.exists(dest):
                reject("File exists", 409)
                return
            print("Uploading file to " + dest)
            
            if not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))

            # Begin section copied from fine-uploader-server (slightly modified)
            if 'qqtotalparts' in attrs and int(attrs['qqtotalparts'][0]) > 1:
                chunked = True
                temp_dest = base_dir(chunk_dir, attrs['qquuid'][0], attrs['qqfilename'][0], str(attrs['qqpartindex'][0]))
                if not os.path.exists(os.path.dirname(temp_dest)):
                    os.makedirs(os.path.dirname(temp_dest))
            else:
                temp_dest = dest
            
            with open(temp_dest, 'wb+') as destination:
                destination.write(attrs['qqfile'][0])
                # chunked
            if chunked and (int(attrs['qqtotalparts'][0]) - 1 == int(attrs['qqpartindex'][0])):
                combine_chunks(attrs['qqtotalparts'][0],
                    attrs['qqtotalfilesize'][0],
                    source_folder=os.path.dirname(temp_dest),
                    dest=dest)
                shutil.rmtree(os.path.dirname(os.path.dirname(temp_dest)))
            # End section copied from fine-uploader-server
        accept()

    # Copied from fine-uploader-server (slightly modified)
    def combine_chunks(total_parts, total_size, source_folder, dest):
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        with open(dest, 'wb+') as destination:
            for i in xrange(int(total_parts)):
                part = os.path.join(source_folder, str(i))
                with open(part, 'rb') as source:
                    destination.write(source.read())

    # Show upload page
    def showUpload(self, subfolder):
        if not config.uploadEnabled:
            self.notAllowed(subfolder)
            return
        folder = base_dir(subfolder)
        up_level = os.path.dirname(subfolder) if subfolder else ""
        nav_folders = folder.split(os.sep)[numBase + 1:]

        r = uptemplate.render(dep=depVersions,
                              subfolder=subfolder,
                              up_level=up_level,
                              nav_folders=nav_folders,
                              page_title="Upload",
                              config=config)
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()
        return

    ## Download a zip file
    def downloadZip(self, subfolder, files):
        base_dir(subfolder) # check for security concern
        print("Downloading Zip in folder: " + subfolder)
        self.send_response(200)
        self.send_header('Content-type', 'application/zip')
        self.send_header('Content-Disposition', 'attachment; filename="%s"' % ((subfolder if subfolder != "" else "Home") + ".zip"))
        self.end_headers()
        with zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED) as z:
            for f in files:
                fullpath = base_dir(subfolder, f)
                if os.path.isdir(fullpath):
                    self._packFolder(z, subfolder, f)
                else:
                    z.write(fullpath, f)
            for chunk in z:
                if chunk:
                    self.wfile.write(chunk)
        self.wfile.flush()
        self.wfile.close()
        print("Download Complete")
        return

    ## Packs a folder inside the ZIP; is recursive
    def _packFolder(self, z, subfolder, target):
        folder = base_dir(subfolder, target)
        folderList = sorted(listdir_dirs(folder, config.strictIgnoreHidden), key=lambda s: s.lower())
        fileList = sorted(listdir_files(folder, config.strictIgnoreHidden), key=lambda s: s.lower())
        for f in fileList:
            fullpath = os.path.join(config.baseFolder, subfolder, target, f)
            fulltarget = os.path.join(target, f)
            z.write(fullpath, arcname=fulltarget)
        for f in folderList:
            self._packFolder(z, subfolder, os.path.join(target, f))

    ## 404
    def notFound(self, subfolder):
        folder = base_dir(subfolder)
        up_level = os.path.dirname(subfolder) if subfolder else ""
        nav_folders = os.path.normpath(os.path.join(config.baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        r = errortemplate.render(dep=depVersions,
                                 subfolder=subfolder,
                                 up_level=up_level,
                                 nav_folders=nav_folders,
                                 page_title="File not found",
                                 msg="The file or folder specified does not exist.",
                                 errorCode=404,
                                 config=config)
        self.send_response(404)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()
    
    ## 403 if path tries to get outside of baseFolder or if user tries to upload when it is disabled
    def notAllowed(self, subfolder):
        folder = os.path.join(config.baseFolder, subfolder)
        up_level = os.path.dirname(subfolder) if subfolder else ""
        nav_folders = os.path.normpath(os.path.join(config.baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        r = errortemplate.render(dep=depVersions,
                                 subfolder=subfolder,
                                 up_level=up_level,
                                 nav_folders=nav_folders,
                                 page_title="Not allowed",
                                 msg="This is not permitted.",
                                 errorCode=403,
                                 config=config)
        self.send_response(403)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()

    ## Shows info
    def info(self):
        authorized = True
        if authstring and self.headers.get('Authorization') != authstring:
            authorized = False
        if self.headers.get("Accept") == "application/json" or self.headers.get("Content-Type") == "application/json":
            r = {"version": __version__, "auth": authstring!=None, "uploads": config.uploadEnabled}
            if authorized:
                r.update({
                         "dependencies": depVersions,
                         "config": config,
                         "uptime": time.mktime(server.uptime.timetuple())
                })
            r = json.dumps(r)
            self.send_response(111)
            self.send_header("Content-type", "application/json;charset=utf-8")
            self.send_header("Content-length", len(r))
            self.end_headers()
            self.wfile.write(r.encode("utf-8"))
            self.wfile.flush()
        else:
            r = infotemplate.render(page_title="Info",
                                    version=__version__,
                                    dep=depVersions,
                                    uptime=server.uptime,
                                    uptime_str=str(datetime.datetime.now()-server.uptime),
                                    authorized=authorized,
                                    config=config
                                    )
            self.send_response(200)
            self.send_header("Content-type", "text/html;charset=utf-8")
            self.send_header("Content-length", len(r))
            self.end_headers()
            self.wfile.write(r.encode("utf-8"))
            self.wfile.flush()


### Basically a HTTPServer with SSL ###
class SecureHTTPServer(HTTPServer):
    def __init__(self, server_address, HandlerClass):
        BaseServer.__init__(self, server_address, HandlerClass)
        self.socket = ssl.SSLSocket(
            sock=socket.socket(self.address_family, self.socket_type),
            ssl_version=ssl.PROTOCOL_TLSv1,
            certfile='server.pem',
            server_side=True)
        self.server_bind()
        self.server_activate()

def setConfig():
    global config, numBase, authstring
    config.baseFolder = os.path.normpath(config.baseFolder)
    numBase = len(list(filter(None, os.path.normpath(config.baseFolder).split(os.sep))))
    if config.username and config.password:
        authstring = "Basic " + base64.b64encode((config.username + ":" + config.password).encode("utf-8")).decode("utf-8")
    else:
        authstring = None

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    
class ThreadedSecureHTTPServer(ThreadingMixIn, SecureHTTPServer):
    """Handle requests in a separate thread."""


class Server(threading.Thread):
    uptime = None
    httpd = None

    def __init__(self):
      threading.Thread.__init__(self)

    def run(self):
        try:
            server_address = ('0.0.0.0', config.port)
            MyHandler.protocol_version = config.protocol
            if config.useSSL:
                self.httpd = ThreadedSecureHTTPServer(server_address, MyHandler)
            else:
                self.httpd = ThreadedHTTPServer(server_address, MyHandler)
            self.uptime = datetime.datetime.now()
            print ("Server Started")
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down server')
            self.httpd.socket.close()

    def shutdown(self):
        print('Shutting down server')
        self.httpd.shutdown()
        self.httpd.socket.close()


# Not being called from GUI; start the server!
if __name__ == '__main__':
    setConfig()
    server = Server()
    server.start()


def quit():
    if server:
        server.shutdown()

atexit.register(quit)
