from select import *
from socket import *
import re

class HttpEpoll:
    def __init__(self,post,port,dir):
        self.post = post
        self.port = port
        self.dir = dir#前端网页的文件夹地址
        self.sockfd = socket()
        self.sockfd.setblocking(False)
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.addr = (self.post,self.port)
        self.sockfd.bind(self.addr)
        self.sockfd.listen(5)#套接字的生成
        self.fd_map = {self.sockfd.fileno():self.sockfd}#创建一个字典

        self.e = epoll()#IO
        self.e.register(self.sockfd,EPOLLIN)#注册关注IO事件

    def send(self,connfd,contant):
        if contant == "/":
            html = self.dir + "/index.html"
        else:
            html = self.dir + contant
        print(html)
        try:
            with open(html,"rb") as f:
                info = f.read()
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type:text/html\r\n"
                response += "Content-Length: %d\r\n"%len(info)
                response += "\r\n"
                response = response.encode() + info
        except:
            response = "HTTP/1.1 404 NotFound\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry......</h1>"
            response = response.encode()
        finally:
            connfd.send(response)

    def handle(self,connfd,even):
        info = connfd.recv(1024).decode() #客户端发送的消息
        try:
            contant = re.match("[A-Z]+\s+(/\S*)",info).group(1)
            print("匹配到的东西：",contant)
        except:
            del self.fd_map[connfd.fileno()]
            self.e.unregister(connfd)
            connfd.close()
            return
        else:
            self.send(connfd,contant)

    def analysis(self): #处理请求
        while True:
            print("等待中。。。")
            events =self.e.poll()
            for fd,even in events: #文件描述符，事件类型
                if fd == self.sockfd.fileno():#判断是不是监听套接字
                    connd,addr = self.fd_map[fd].accept()#生成连接套接字
                    print("connd from:",addr)
                    connd.setblocking(False)
                    self.e.register(connd,EPOLLIN)#注册关注IO事件
                    self.fd_map[connd.fileno()] = connd#维护字典
                else:
                    self.handle(self.fd_map[fd],even)

    def start(self):
        self.analysis()

if __name__ == '__main__':
    post = "0.0.0.0"
    port = 8888
    dir = "../day17/static"
    ht = HttpEpoll(post,port,dir)
    ht.start()
