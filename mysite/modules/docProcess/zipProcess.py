#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
import zipfile
import os
import chardet

'''
在windows下压缩到linux解压存在文件名编码问题（gb2312->utf-8）
'''


# 此函数可作为通用解压函数：在windows下压缩到linux解压存在文件名编码问题（gb2312->utf-8），通过以下代码解决
def unzip(filepath,filename,fullpath=None):
    # 以下代码是为了增加可靠性
    if fullpath:
        realpath = fullpath
    else:
        if not filepath.endswith('/'):
            filepath += '/'
        realpath = filepath+filename
    # 功能代码
    with zipfile.ZipFile(realpath, 'r') as f:
        for name in f.namelist():  # 递归获取压缩包内所有的文件或目录名（具有相对压缩包位置的完整路径）
            try:  # 如果detect出错则表明name本来就是unicode无需解码
                origin_encoding = chardet.detect(name)
                utf8name = filepath+name.decode(origin_encoding['encoding'])  # 获得解码后的正确名称
            except:
                utf8name = filepath + name
            pathname = os.path.dirname(utf8name)
            if not os.path.exists(pathname) and pathname != "":
                os.makedirs(pathname)
            data = f.read(name)  # 直接从压缩包中读取文件，不经过解压过程（解压过程不支持中文的bug）
            if not os.path.exists(utf8name):
                fo = open(utf8name, "w")
                fo.write(data)
                fo.close()


# 此函数可作为通用压缩函数：压缩部署后的文件夹，便于后续打包下载
def zip(filepath,newname=None):
    if newname is None:
        newname = filepath + '.zip'
    z = zipfile.ZipFile(newname, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(filepath):
        fpath = dirpath.replace(filepath, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
    z.close()
