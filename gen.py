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
    with open(f'crunchyroll/Sousou no Frieren S01E{episode:02d}.vtt', 'rt') as vtt:
        with Popen(['ffmpeg', '-i', '-', '-f', 'ass', 'pipe:1'], stdin=PIPE, stdout=PIPE, stderr=DEVNULL, encoding='UTF-8') as ffmpeg:
            ffmpeg.stdin.write('WEBVTT\n')
            content = False
            for line in vtt:
                if content:
                    ffmpeg.stdin.write(REGEX_VTT.sub('', line))
                elif line == '}\n':
                    content = True
            ass_dialogs = filter(lambda line: line.startswith('Dialogue: '), ffmpeg.communicate()[0].split('\n'))
    with open(f'9volt/Sousou no Frieren S01E{episode:02d}.ass', 'rt') as ass:
        ass_orig = [line.rstrip('\n') for line in ass.readlines()]
    italics = []
    for line in ass_orig:
        if line.startswith('Dialogue: '):
            fields = line.split(',')
            if fields[3] == 'Italics':
                italics.append((parsetime(fields[1]), parsetime(fields[2])))
    with open(f'out/Sousou no Frieren S01E{episode:02d}.ass', 'wt') as out:
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
                    if fields[9] != '♪' and not (fields[9][0] == '[' and fields[9][-1] == ']'):
                        for it in italics:
                            if it[0] <= begin <= it[1] or it[0] <= end <= it[1] or begin <= it[0] <= end:
                                phrase = phrase.replace(',Default,', ',Italics,', 1)
                                break
                    phrase = phrase \
                        .replace('AuBerst', 'Äußerst') \
                        .replace('Auberst', 'Äußerst') \
                        .replace('Ubel', 'Übel') \
                        .replace('UBEL', 'ÜBEL') \
                        .replace('Lugner', 'Lügner') \
                        .replace('LUGNER', 'LÜGNER') \
                        .replace('Tur.', 'Tür.') \
                        .replace('Dunste', 'Dünste') \
                        .replace('DUNSTE', 'DÜNSTE') \
                        .replace('Bose', 'Böse')
                    out.write(phrase + '\n')
                insert = False
            if line == '[Events]':
                insert = True


if __name__ == '__main__':
    os.chdir(Path(sys.argv[0]).resolve().parent)
    for i in range(1, 29):
        generate(i)
