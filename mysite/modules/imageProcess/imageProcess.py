#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import click
from io import BytesIO
from PIL import Image,ImageFilter, ImageOps


'''
PIL只处理位图

FORMAT文件格式:
    JPEG:有损压缩RGB位图
    PNG:无损压缩RGBA位图
    BMP:原始RGB位图
    GIF:无损压缩CMYK位图可动态

MODE像素通道模式:
    1：1位像素，表示黑和白，但是存储的时候每个像素存储为8bit。
    L：8位像素，表示黑和白。
    P：8位像素，使用调色板映射到其他模式。
    RGB：3x8位像素，为真彩色。
    RGBA：4x8位像素，有透明通道的真彩色。
    CMYK：4x8位像素，颜色分离。
    YCbCr：3x8位像素，彩色视频格式。
    I：32位整型像素。
    F：32位浮点型像素。
    PIL也支持一些特殊的模式，包括RGBX（有padding的真彩色）和RGBa（有自左乘alpha的真彩色）。

SIZE尺寸:
    直角坐标，原点在左上角为(0,0)，每个像素（px=pixel）的宽高为1x1，左上角的像素的中心点是(0.5,0.5)
    尺寸值：(x-width,y-height)
    位置坐标：(x-pos,y-pos)

BANDS通道:
    每个像素点的数据单元，比如png有四通道(R,G,B,A)

'''


class ImageProcess:
    def __init__(self,image_path1):
        self.im1 = Image.open(image_path1)
        self.imo = self.im1

    @staticmethod
    def func_liangdu_jia(c):
        return c*1.3

    @staticmethod
    def func_liangdu_jian(c):
        return c*0.7

    def info(self,image_path2):
        info_str1 = 'format:'+str(self.im1.format)+\
                   '\nmode:'+str(self.im1.mode)+\
                   '\nsize:'+str(self.im1.size)+ \
                   '\nbands:' + str(self.im1.getbands())
        info_str2 = ''
        if image_path2:
            im2 = Image.open(image_path2)
            info_str2 += 'format:' + str(im2.format) + \
                       '\nmode:' + str(im2.mode) + \
                       '\nsize:' + str(im2.size)+ \
                       '\nbands:' + str(im2.getbands())
        return info_str1,info_str2

    def blend(self,image_path2,blend_alpha):
        if image_path2:
            im2 = Image.open(image_path2)
            if im2.size != self.imo.size:
                im2c = im2.resize(self.imo.size)
            else:
                im2c = im2
            self.imo = Image.blend(self.imo,im2c,blend_alpha)  # out = image1 *(1.0 - alpha) + image2 * alpha

    def composite(self,image_path2,composite_path):
        if image_path2 and composite_path:
            im2 = Image.open(image_path2)
            if im2.size != self.imo.size:
                im2c = im2.resize(self.imo.size)
            else:
                im2c = im2
            mask = Image.open(composite_path)
            if mask.size != self.imo.size:
                maskc = mask.resize(self.imo.size)
            else:
                maskc = mask
            self.imo = Image.composite(self.imo,im2c,maskc)  # out = image1 + image2 * mask[alpha]

    def eval(self,eval_liangdu=0,eval_fanse=False,eval_heibai=False,eval_erzhi=False):
        if eval_liangdu == 1:
            self.imo = Image.eval(self.imo,self.func_liangdu_jia)
        if eval_liangdu == -1:
            self.imo = Image.eval(self.imo,self.func_liangdu_jian)
        if eval_liangdu == 0:
            pass
        if eval_fanse:
            self.imo = ImageOps.invert(self.imo)
        if eval_heibai:
            self.imo = self.imo.convert('L')
        if eval_erzhi:
            self.imo = self.imo.convert('1')

    def filter(self,filter_blur=False,filter_contour=False):
        if filter_blur:
            self.imo = self.imo.filter(ImageFilter.GaussianBlur)
        if filter_contour:
            self.imo = self.imo.filter(ImageFilter.CONTOUR)

    def convert_image(self,image_path2='',info=False,blend=False,composite=False,eval=False,filter=False,
                      blend_alpha=0.5,
                      composite_path='06.png',
                      eval_liangdu=0,eval_fanse=False,eval_heibai=False,eval_erzhi=False,
                      filter_blur=False,filter_contour=False):
        if info:
            return self.info(image_path2)
        if blend:
            self.blend(image_path2,blend_alpha)
        if composite:
            self.composite(image_path2,composite_path)
        if eval:
            self.eval(eval_liangdu,eval_fanse,eval_heibai,eval_erzhi)
        if filter:
            self.filter(filter_blur,filter_contour)
        image_data = BytesIO()  # 将图片数据暂存到内存中
        self.imo.save(image_data, 'jpeg')
        return image_data.getvalue()

    def convert_image_cli(self,output_path,image_path2,op,
                        blend_alpha=0.3,
                        composite_path='06.png',
                        eval_liangdu=0,eval_fanse=False,eval_heibai=True,eval_erzhi=False,
                        filter_blur=False,filter_contour=False):
        if op == 'info':
            imo = self.info(image_path2)
            print(imo)
        elif op == 'blend':
            self.blend(image_path2,blend_alpha)
        elif op == 'composite':
            self.composite(image_path2,composite_path)
        elif op == 'eval':
            self.eval(eval_liangdu, eval_fanse, eval_heibai, eval_erzhi)
        elif op == 'filter':
            self.filter(filter_blur,filter_contour)
        self.imo.save(output_path, 'jpeg')


if __name__ == '__main__':
    #命令行参数工具click
    @click.command()
    @click.option("-p", default='info', type=click.Choice(['info','blend', 'composite','filter','eval']), help=u'操作选项')
    # @click.option("-e", is_flag=True, help=u'二值化')  # is_flag以参数名控制，不需要写参数值
    @click.option("-o",default='', help=u'输出文件名')
    @click.argument("filename1")
    @click.argument("filename2",default='')
    def convert(filename1,filename2,o,p):
        converter = ImageProcess(filename1)
        if o:
            converter.convert_image_cli(os.path.join('output',o),filename2,p)
        else:
            converter.convert_image_cli(os.path.join('output',filename1),filename2, p)
    convert()
