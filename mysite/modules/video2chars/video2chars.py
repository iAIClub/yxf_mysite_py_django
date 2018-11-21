#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pkg_resources import resource_stream
import numpy
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw
import click

"""参考原作者代码https://github.com/ryan4yin"""
"""视频转码过程非常耗CPU资源，只能线下提前转好，线上服务器不可使用"""

class Video2Chars:
    def __init__(self, video_path, fps, pixels, chars_width, t_start=0, t_end=None):
        """
        :param video_path: 字符串, 视频文件的路径
        :param fps: 生成的视频的帧率
        :param pixels:用于充当像素的字符
        :param chars_width: 字符的宽度（以像素记），会影响最终视频的分辨率。
        :param t_start, t_end: 视频的开始时间和结束时间，只处理指定时间段的视频。
        """
        # 加载视频,并截取
        video_clip = VideoFileClip(video_path).subclip(t_start, t_end)
        self.fps = fps
        #像素形状（按照视觉由深到浅排序，后面用于灰度值）
        self.pixels = pixels if pixels else \
            "MNEFTmneotli\"'. " #16阶
        self.chars_width = chars_width
        self.chars_height = int(chars_width/video_clip.aspect_ratio)#宽高比
        self.video_clip:VideoClip = video_clip.resize((self.chars_width, self.chars_height))
        # 字体相关
        font_fp = resource_stream("video2chars", "DroidSansMono.ttf")
        self.font = ImageFont.truetype(font_fp, size=14)  # 使用等宽字体
        self.font_width = sum(self.font.getsize("a")) // 2  # 为了保证像素宽高一致，均取宽高的平均值
        # 产生的视频的宽高（以像素记）
        self.video_size = int(self.chars_width * self.font_width), int(self.chars_height * self.font_width)

    def get_char_by_gray(self, gray):
        """通过灰度值从 pixels 中挑选字符，充当字符动画中的‘像素’"""
        percent = gray / 255  # 转换到 0-1 之间
        index = int(percent * (len(self.pixels) - 1))  # 拿到index“颜色值”
        return self.pixels[index]

    def get_chars_frame(self, t):
        """将每一帧图片转换为字符画"""
        # 获取到图像
        img_np = self.video_clip.get_frame(t)
        img = Image.fromarray(img_np, "RGB")
        img_gray = img.convert(mode="L")
        # 新建画布
        img_chars = Image.new("RGB", self.video_size, color="white")
        brush = ImageDraw.Draw(img_chars)  # 画笔
        for y in range(self.chars_height):
            for x in range(self.chars_width):
                r, g, b = img_np[y][x]
                gray = img_gray.getpixel((x, y))
                char = self.get_char_by_gray(gray)
                position = x * self.font_width, y * self.font_width  # x 横坐标（宽），y纵坐标（高，而且向下为正）
                brush.text(position, char, fill=(r, g, b), font=self.font)
        return numpy.array(img_chars)

    def generate_chars_video(self):
        """生成字符视频对象"""
        clip = VideoClip(self.get_chars_frame, duration=self.video_clip.duration)
        return clip.set_fps(self.fps).set_audio(self.video_clip.audio)


if __name__ == '__main__':
    #命令行参数工具click
    @click.command()
    @click.option("--chars_width", default=150, help='The width of the generated video, in characters, default to 200')
    @click.option("--fps", default=8, help='frames per second, defaults to 8')
    @click.option("--pixels", default=None, type=str, help='the chars sequence used to generate character animation')
    @click.option("--t_start", default=0, help="the start time that the video needs to be converted(in seconds)")
    @click.option("--t_end", default=None, type=int, help="the end time that the video needs to be converted(in seconds)")
    @click.option("--output", default="output.mp4", help='output to a file with this name, default to "output.mp4"')
    @click.argument("filename")
    def convert(filename, chars_width, fps, pixels, output, t_start, t_end):
        converter = Video2Chars(video_path=filename,
                                fps=fps,
                                chars_width=chars_width,
                                t_start=t_start,
                                t_end=t_end,
                                pixels=pixels)

        clip = converter.generate_chars_video()
        clip.write_videofile(os.path.join('output',filename))
    convert()
