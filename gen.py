#!/usr/bin/env python3

import sys
import os
import re
from pathlib import Path
from subprocess import Popen, PIPE, DEVNULL


REGEX_VTT = re.compile('</?(Default|b)>')


def parsetime(t):
    c = t.split('.')[1]
    h, m, s = t.split('.')[0].split(':')
    return ((h*60 + m)*60 + s)*100 + c


def generate(episode):
    with open(f'Subtitles/Crunchyroll/[SubsPlease] Sousou no Frieren - {episode:02d} [WEB-DL 1080p x264 DDP].vtt', 'rt') as vtt:
        with Popen(['ffmpeg', '-i', '-', '-f', 'ass', 'pipe:1'], stdin=PIPE, stdout=PIPE, stderr=DEVNULL, encoding='UTF-8') as ffmpeg:
            ffmpeg.stdin.write('WEBVTT\n')
            content = False
            for line in vtt:
                if content:
                    ffmpeg.stdin.write(REGEX_VTT.sub('', line))
                elif line == '}\n':
                    content = True
            ass_dialogs = filter(lambda line: line.startswith('Dialogue: '), ffmpeg.communicate()[0].split('\n'))
    with Popen(['ffmpeg', '-i', f'[SubsPlease] Sousou no Frieren - {episode:02d} [WEB-DL 1080p x264 DDP].mkv', '-map', '0:s:3', '-f', 'ass', 'pipe:1'], stdin=DEVNULL, stdout=PIPE, stderr=PIPE, encoding='UTF-8') as ffmpeg:
        ass_orig = ffmpeg.communicate()[0].split('\n')
    italics = []
    for line in ass_orig:
        if line.startswith('Dialogue: '):
            fields = line.split(',')
            if fields[3] == 'Italics':
                italics.append((parsetime(fields[1]), parsetime(fields[2])))
    with open(f'Subtitles/Out/[SubsPlease] Sousou no Frieren - {episode:02d} [WEB-DL 1080p x264 DDP].ass', 'wt') as out:
        insert = False
        for line in ass_orig:
            if line.startswith('Dialogue: '):
                fields = line.split(',')
                if fields[3] in ['Default', 'Italics', 'Btm-Alt']:
                    continue
                if fields[3] == 'Top-Alt' and episode not in [1]:
                    continue
            out.write(line + '\n')
            if insert:
                for phrase in ass_dialogs:
                    fields = phrase.split(',')
                    begin = parsetime(fields[1])
                    end = parsetime(fields[2])
                    if fields[9] != '♪':
                        for it in italics:
                            if it[0] <= begin <= it[1] or it[0] <= end <= it[1]:
                                phrase = phrase.replace(',Default,', ',Italics,', 1)
                                break
                    phrase = phrase \
                        .replace('AuBerst', 'Äußerst') \
                        .replace('Auberst', 'Äußerst') \
                        .replace('Ubel', 'Übel') \
                        .replace('UBEL', 'ÜBEL')
                    out.write(phrase + '\n')
                insert = False
            if line == '[Events]':
                insert = True


if __name__ == '__main__':
    os.chdir(Path(sys.argv[0]).resolve().parent.parent.parent)
    for i in range(1, 29):
        generate(i)
