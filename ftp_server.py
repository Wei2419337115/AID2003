"""
author:Levi
email: lvze@tedu.cn
ftp文件服务器服务端模型
"""

from socket import *
from threading import Thread
import os
from time import sleep

# 全局变量
HOST = "0.0.0.0"
PORT = 7779
ADDR = (HOST,PORT)
FTP = "/home/tarena/student/Linux/"  # 文件库


# 自定义线程类--》编写具体方法应对客户端各种请求
class FTPServer(Thread):
    def __init__(self,connfd):
        self.connfd = connfd
        super().__init__()

    def do_list(self):
        # 判断文件库是否为空
        file_list = os.listdir(FTP)
        # 给客户端反馈
        if not file_list:
            self.connfd.send(b'Fail')
            return # 结束
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
            # 发送文件列表  \n作为消息边界防止粘包
            files = '\n'.join(file_list)
            self.connfd.send(files.encode())

    def do_get_file(self,file_name):
        try:
            f = open(FTP + file_name,"rb") #判斷文件是否存在
            self.connfd.send(b"OK")
            sleep(0.1)
        except:
            self.connfd.send(b"flase")
            return
        while True:
            words = f.read(1024)
            if not words:
                sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(words)



    # 线程执行内容

    def do_up_file(self,file_name):
        if file_name in os.listdir(FTP):
            self.connfd.send(B"False")
            return
        else:
            self.connfd.send(b"OK")
            with open(FTP+file_name,"wb") as f:
                while True:
                    data = self.connfd.recv(1024 * 10)
                    if data == b"##":
                        break
                    f.write(data)

    def do_quit(self):
        self.connfd.close()

    def run(self):
        # 循环接收请求分情况处理
        while True:
            data = self.connfd.recv(1024).decode() # 接收请求
            if data == "quit":
                self.do_quit()
                return
            elif data == 'L':
                self.do_list()
            elif data[0] == 'D':
                self.do_get_file(data.split(" ")[-1])
            elif data[0] == "U":
                self.do_up_file(data.split(" ")[-1])


def main():
    # 创建tcp套接字
    sockfd = socket()
    sockfd.bind(ADDR)
    sockfd.listen(5)

    print("Listen the port %d"%PORT)
    # 循环处理客户端链接
    while True:
        try:
            connfd,addr = sockfd.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            print("服务结束")
            break

        # 为客户端创建分之线程
        t = FTPServer(connfd)
        t.setDaemon(True)  # 分之线程随主线程退出
        t.start()

    sockfd.close()

if __name__ == '__main__':
    main()