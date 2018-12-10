# -*- coding: utf-8 -*-
from __future__ import unicode_literals,print_function
import os
import mammoth
import zipfile
import os
import shutil
import chardet
import subprocess
import logging

'''
在windows下压缩到linux解压存在文件名编码问题（gb2312->utf-8）
pandoc不支持直接转换docx文档，先用mammoth把docx转换为html（保留表格），再用pandoc转换为md(markdown_strict保留html原文)
mammoth可选择图片内嵌或存到外部（为了保证文档的完整性，建议内嵌，如此也降低了可编辑性和访问速度）
shell执行mammoth，文件名不能带有&字符（shell本身的问题，特殊符号）
'''


# 此函数可作为通用解压函数：在windows下压缩到linux解压存在文件名编码问题（gb2312->utf-8），通过以下代码解决
def unzip(filepath,filename):
    with zipfile.ZipFile(filepath+filename, 'r') as f:
        for name in f.namelist():  # 递归获取压缩包内所有的文件或目录名（具有相对压缩包位置的完整路径）
            origin_encoding = chardet.detect(name)
            utf8name = filepath+name.decode(origin_encoding['encoding'])  # 获得解码后的正确名称
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


# 此函数只执行单个文件，若要执行整个目录则需要在外部循环调用
def execute_docx(file_from):
    curPath = os.path.dirname(file_from)
    filename = file_from.split('/')[-1].split('.')[0]
    targetPath = curPath # + os.path.sep + filename
    file_middle = targetPath + os.path.sep + filename + '.html'
    file_to = targetPath + os.path.sep + filename + '.md'
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    # execute mammoth->html
    p = subprocess.Popen('mammoth --output-format html {0} {1}'.format(file_from,file_middle)
                         , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    info = file_from
    logging.error(info)
    err = p.stderr.readlines()
    logging.error(err)
    # execute pandoc->md
    __execute_pandoc(file_middle,file_to)


# 由execute_doc()调用，docx转为html后再调用pandoc转为md
def __execute_pandoc(file_middle,file_to):
    p = subprocess.Popen('pandoc -f html -t markdown_strict {0} -o {1}'.format(file_middle,file_to)
                         , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        err = p.stderr.readlines()
        logging.error(err)
