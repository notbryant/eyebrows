# General socket/connection stuff
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
import urllib.parse
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
sys.path.insert(0, 'lib')
import cgi_tweaked as cgi
import mako  # for the version
from mako.template import Template
from mako.lookup import TemplateLookup
sys.path.insert(0, 'lib/zipstream')
import json
import math
# Used for zip file generation
import zipstream
# Project files
from icontypes import fileIcons
from utils import *
# Config
baseFolder = os.path.expanduser("~")
port = 8080
hideBarsDelay = 3000
protocol = "HTTP/1.0"
useSSL = True
username = "admin"
password = "admin"
ignoreHidden = False
strictIgnoreHidden = False
useDots = False
sortFoldersFirst = True
uploadEnabled = True
from config import *
baseFolder = os.path.normpath(baseFolder)

# Variables that are automatically set. DO NOT TOUCH
__version__ = 1.0
depVersions = {"python": ".".join(str(x) for x in sys.version_info[0:3]),
               "mako": mako.__version__,
               "zipstream": zipstream.__version__,
               "fineuploader": "4.2.1",
               "jquery": "1.10.2",
               "bootstrap": "3.0.3",
               "fontawesome": "4.0.3",
               "swipebox": "1.2.1"}

if os.name == 'nt':
    try:
        import win32api
        import win32con
        depVersions["pywin32"] = win32api.GetFileVersionInfo(win32api.__file__, "\\")['FileVersionLS'] >> 16
    except ImportError:
        ignoreHidden = False


numBase = len(os.path.normpath(baseFolder).split(os.sep)) - 1
if username and password:
    authstring = "Basic " + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8")
else:
    authstring = None
maintemplate = Template(filename='views/main.html', lookup=TemplateLookup(directories=['views/']))
uptemplate = Template(filename='views/upload.html', lookup=TemplateLookup(directories=['views/']))
errortemplate = Template(filename='views/error.html', lookup=TemplateLookup(directories=['views/']))
infotemplate = Template(filename='views/info.html', lookup=TemplateLookup(directories=['views/']))
chunk_dir = "chunks"


### Main class that handles everything ###
class MyHandler(SimpleHTTPRequestHandler):
    def __init__(self, req, client_addr, server):
        SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)

    def send_401(self):
        print("Sending 401")
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Log in\"')
        if protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        self.end_headers()

    ## Handle Get requests
    def do_GET(self):
        theArg = urllib.parse.unquote(self.path.split("?")[0])[1:]
        if theArg == "~":
            return self.info()
        # paths that start with /~ refer to the directory
        if theArg.startswith("~/css") or theArg.startswith('~/js') or theArg.startswith('~/img'):
            return self.getResource(theArg[2:])
        if authstring and self.headers.get('Authorization'):
            token = self.headers.get('Authorization')[len("Basic "):]
            print("Attempted login: " + base64.b64decode(token.encode("utf-8")).decode("utf-8"))
        if authstring and self.headers.get('Authorization') != authstring:
            return self.send_401()  # authorization required

        parameters = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        pathVar = os.path.join(baseFolder, theArg)
        # paths that start with /~ refer to the directory
        #if theArg.startswith("~"):
        #    return self.getResource(theArg[2:])
        # Check for existence
        if not os.path.exists(pathVar):
            return self.notFound(theArg)
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

    ## Serve a resource that lives in the same folder as Eyebrows, such as CSS or JS
    def getResource(self, relPath):
        print("Resourcing: " + relPath)
        f = open(os.path.normpath(relPath), 'rb')
        self.send_response(200)

        dat = f.read()
        self.send_header("Content-length", len(dat))
        if protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        self.end_headers()
        self.wfile.write(dat)
        self.wfile.flush()
        f.close()

    ## Download or view a file when requested from a GET
    def downloadFile(self, relPath, parameters):
        print("Downloading: " + relPath)
        if "i" in parameters and parameters["i"]:
            SimpleHTTPRequestHandler.do_GET(self)
            return

        derp, ext = os.path.splitext(relPath)
        ext = ext[1:].lower()
        f = open(os.path.join(baseFolder, relPath), 'rb')
        self.send_response(200)
        if ext == "html" or ext == "htm":
            self.send_header('Content-type', 'text/html;charset=utf-8')
        dat = f.read()
        self.send_header("Content-length", len(dat))
        if protocol == "HTTP/1.1":
            self.send_header('Connection', 'Close')
        self.end_headers()
        self.wfile.write(dat)
        self.wfile.flush()
        f.close()

    ## Send the data back as JSON
    def doJSON(self, subfolder):
        folder = os.path.join(baseFolder, subfolder)
        if os.path.islink(folder):
            print("Found a symlink")
            folder = os.path.realpath(folder)
        page_title = os.path.basename(subfolder)
        folderList = sorted(listdir_dirs(folder, strictIgnoreHidden or ignoreHidden), key=lambda s: s.lower())
        fileList = sorted(listdir_files(folder, strictIgnoreHidden or ignoreHidden), key=lambda s: s.lower())
        print("json: " + json.dumps(folderList))
        
        r = []
        
        for f in folderList:
            r.append({"name": f,
                      "size": 0,
                      "icon": "folder",
                      "time": math.floor(os.path.getmtime(os.path.join(folder, f)))
                      })
            
        for f in fileList:
            derp, ext = os.path.splitext(f)
            r.append({"name": f,
                      "size": os.path.getsize(os.path.join(folder, f)),
                      "icon": fileIcons[ext[1:]] if (ext[1:] in fileIcons) else "file-o", 
                      "time": os.path.getmtime(os.path.join(folder, f))
                      })
        
        r = json.dumps(r)
        self.send_response(200)
        self.send_header("Content-type", "application/json;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()

    ## Display a folder
    def doFolder(self, subfolder):
        folder = os.path.join(baseFolder, subfolder)
        if os.path.islink(folder):
            print("Found a symlink")
            folder = os.path.realpath(folder)

        up_level = os.path.dirname(subfolder) if subfolder else ""
        page_title = os.path.basename(subfolder)
        nav_folders = os.path.normpath(os.path.join(baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        itemList = sorted(listdir(folder, strictIgnoreHidden or ignoreHidden),
                          key=((lambda s: [-s[1], s[0].lower()]) if sortFoldersFirst else (lambda s: s[0].lower())))
        r = maintemplate.render(dep=depVersions,
                                subfolder=subfolder,
                                up_level=up_level,
                                page_title=page_title,
                                nav_folders=nav_folders,
                                itemList=itemList,
                                hideBarsDelay=hideBarsDelay,
                                fileIcons=fileIcons,
                                baseFolder=baseFolder,
                                useDots=useDots)
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
        print("Posted: " + self.path)
        print(self.headers)
        if self.path == "/~":
            post_data = urllib.parse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
            print(post_data)
            self.downloadZip(post_data['subfolder'][0] if 'subfolder' in post_data else "", post_data['items'])
        else:
            self.uploadFile()

    def uploadFile(self):
        if not uploadEnabled:
            self.notAllowed(self.path[1:])
            return
        print("Ok uploading file")
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        print("Parsed header")
        attrs = cgi.parse_multipart(self.rfile, pdict)  # qquuid, qqfilename, qqtotalfilesize, qqfile
        print("Parsed multipart")
        print(attrs['qqfilename'])
        subfolder = self.path[1:]
        dest = os.path.join(baseFolder, subfolder, attrs['qqfilename'][0].decode('utf-8'))
        chunked = False
        print("Uploading file to " + dest)
        if os.path.exists(dest):
            r = '{"error": "File exists", "preventRetry": true}'
            self.send_response(409)
            self.send_header("Content-type", "text/plain;charset=utf-8")
            self.send_header("Content-length", len(r))
            self.end_headers()
            self.wfile.write(r.encode("utf-8"))
            self.wfile.flush()
        else:
            r = '{"success": true}'
            self.send_response(200)
            self.send_header("Content-type", "text/plain;charset=utf-8")
            self.send_header("Content-length", len(r))
            self.end_headers()
            self.wfile.write(r.encode("utf-8"))
            self.wfile.flush()
        # Begin section copied from fine-uploader-server (slightly modified)
        if 'qqtotalparts' in attrs and int(attrs['qqtotalparts'][0]) > 1:
            chunked = True
            dest_folder = os.path.join(chunk_dir, attrs['qquuid'][0])
            dest = os.path.join(dest_folder, attrs['qqfilename'][0], str(attrs['qqpartindex'][0]))
            # save dat file
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        with open(dest, 'wb+') as destination:
            destination.write(attrs['qqfile'][0])
            # chunked
        if chunked and (int(attrs['qqtotalparts'][0]) - 1 == int(attrs['qqpartindex'][0])):
            combine_chunks(attrs['qqtotalparts'][0],
                attrs['qqtotalfilesize'][0],
                source_folder=os.path.dirname(dest),
                dest=os.path.join(app.config['UPLOAD_DIRECTORY'], attrs['qquuid'][0],
                    attrs['qqfilename'][0]))
            shutil.rmtree(os.path.dirname(os.path.dirname(dest)))
        # End section copied from fine-uploader-server

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
        if not uploadEnabled:
            self.notAllowed(subfolder)
            return
        folder = os.path.join(baseFolder, subfolder)
        up_level = os.path.dirname(subfolder) if subfolder else ""
        nav_folders = os.path.normpath(os.path.join(baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        r = uptemplate.render(dep=depVersions,
                              subfolder=subfolder,
                              up_level=up_level,
                              nav_folders=nav_folders,
                              baseFolder=baseFolder,
                              useDots=useDots,
                              page_title="Upload")
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()
        return

    ## Download a zip file
    def downloadZip(self, subfolder, files):
        print("Downloading Zip in folder: " + subfolder)
        self.send_response(200)
        self.send_header('Content-type', 'application/zip')
        self.send_header('Content-Disposition', 'attachment; filename="%s"' % ((subfolder if subfolder != "" else "Home") + ".zip"))
        self.end_headers()
        with zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED) as z:
            for f in files:
                fullpath = os.path.join(baseFolder, subfolder, f)
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
        folder = os.path.join(baseFolder, subfolder, target)
        folderList = sorted(listdir_dirs(folder, strictIgnoreHidden), key=lambda s: s.lower())
        fileList = sorted(listdir_files(folder, strictIgnoreHidden), key=lambda s: s.lower())
        for f in fileList:
            fullpath = os.path.join(baseFolder, subfolder, target, f)
            fulltarget = os.path.join(target, f)
            z.write(fullpath, arcname=fulltarget)
        for f in folderList:
            self._packFolder(z, subfolder, os.path.join(target, f))

    ## 404
    def notFound(self, subfolder):
        folder = os.path.join(baseFolder, subfolder)
        up_level = os.path.dirname(subfolder) if subfolder else ""
        nav_folders = os.path.normpath(os.path.join(baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        r = errortemplate.render(dep=depVersions,
                                 subfolder=subfolder,
                                 up_level=up_level,
                                 nav_folders=nav_folders,
                                 baseFolder=baseFolder,
                                 useDots=useDots,
                                 page_title="File not found",
                                 msg="The file or folder specified does not exist.",
                                 errorCode=404)
        self.send_response(404)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-length", len(r))
        self.end_headers()
        self.wfile.write(r.encode("utf-8"))
        self.wfile.flush()
    
    ## 403 (currently used for saying that uploading is not allowed
    def notAllowed(self, subfolder):
        folder = os.path.join(baseFolder, subfolder)
        up_level = os.path.dirname(subfolder) if subfolder else ""
        nav_folders = os.path.normpath(os.path.join(baseFolder, subfolder)).split(os.sep)[numBase + 1:]

        r = errortemplate.render(dep=depVersions,
                                 subfolder=subfolder,
                                 up_level=up_level,
                                 nav_folders=nav_folders,
                                 baseFolder=baseFolder,
                                 useDots=useDots,
                                 page_title="Not allowed",
                                 msg="This functionality has been disabled.",
                                 errorCode=404)
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
            r = {"version": __version__, "auth": authstring!=None, "uploads": uploadEnabled}
            if authorized:
                r.update({
                         "dependencies": depVersions,
                         "config": {
                             "port": port,
                             "useSSL": useSSL,
                             "protocol": protocol,
                             "hideBarsDelay": hideBarsDelay,
                             "ignoreHidden": ignoreHidden,
                             "strictIgnoreHidden": strictIgnoreHidden,
                             "useDots": useDots,
                             "sortFoldersFirst": sortFoldersFirst,
                         },
                         "uptime": time.mktime(uptime.timetuple())
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
                                    # App Info
                                    version=__version__,
                                    # Sys info
                                    depVersions=depVersions,
                                    # Config
                                    port=port,
                                    useSSL=useSSL,
                                    protocol=protocol,
                                    baseFolder=baseFolder,
                                    hideBarsDelay=hideBarsDelay,
                                    username=username,
                                    password=password,
                                    ignoreHidden=ignoreHidden,
                                    strictIgnoreHidden=strictIgnoreHidden,
                                    useDots=useDots,
                                    sortFoldersFirst=sortFoldersFirst,
                                    # etc
                                    uptime=uptime,
                                    uptime_str=str(datetime.datetime.now()-uptime),
                                    authorized=authorized
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

uptime = datetime.datetime.now()
try:
    server_address = ('0.0.0.0', port)
    MyHandler.protocol_version = protocol
    if useSSL:
        httpd = SecureHTTPServer(server_address, MyHandler)
    else:
        httpd = HTTPServer(server_address, MyHandler)
    print ("Server Started")
    httpd.serve_forever()
except KeyboardInterrupt:
    print('Shutting down server')
    httpd.socket.close()
