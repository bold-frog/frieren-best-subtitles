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
    with open(f'crunchyroll/Sousou no Frieren S01E{episode:02d}.vtt', 'rt', encoding='utf-8') as vtt:
        with Popen(['ffmpeg', '-i', '-', '-f', 'ass', 'pipe:1'], stdin=PIPE, stdout=PIPE, stderr=DEVNULL, encoding='UTF-8') as ffmpeg:
            ffmpeg.stdin.write('WEBVTT\n')
            content = False
            for line in vtt:
                if content:
                    ffmpeg.stdin.write(REGEX_VTT.sub('', line))
                elif line == '}\n':
                    content = True
            ass_dialogs = filter(lambda line: line.startswith('Dialogue: '), ffmpeg.communicate()[0].split('\n'))
    with open(f'9volt/Sousou no Frieren S01E{episode:02d}.ass', 'rt', encoding='utf-8') as ass:
        ass_orig = [line.rstrip('\n') for line in ass.readlines()]
    italics = []
    for line in ass_orig:
        if line.startswith('Dialogue: '):
            fields = line.split(',')
            if fields[3] == 'Italics':
                italics.append((parsetime(fields[1]), parsetime(fields[2])))
    with open(f'out/Sousou no Frieren S01E{episode:02d}.ass', 'wt', encoding='utf-8') as out:
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
                    if episode == 3:
                        phrase = phrase \
                            .replace('She seemed so conflicted.', 'She seems so conflicted.')
                        if phrase.endswith(',-So they\'re adventurers, then.\\N-After a long day\'s work,'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1).replace(',-So they\'re adventurers, then.\\N-After a long day\'s work,', ',So they\'re adventurers, then.')
                        elif phrase.endswith(',Still, I\'d say "rugged"'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1)
                        elif phrase.endswith(',is an understatement.'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1)
                        elif phrase.endswith(',-[FERN]They\'re terrifying.\\N-Gotta live a little, right?'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1).replace(',-[FERN]They\'re terrifying.\\N-Gotta live a little, right?', ',[FERN]They\'re terrifying.')
                    elif episode == 4:
                        if phrase.endswith(',This is going to be\\Nan uphill battle.'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1)
                    elif episode == 5:
                        if phrase.endswith(',-[FERN] It knows.\\N-The path of the mage called,'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1).replace('-[FERN] It knows.', '{\\i1}-[FERN] It knows.{\\i0}')
                        elif phrase.endswith(',your love for magic\\Nhas been clear.'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1)
                        elif phrase.endswith(',-The first time I saw...\\N-[FERN] It knows all of them,'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1).replace('-[FERN] It knows all of them,', '{\\i1}-[FERN] It knows all of them,{\\i0}')
                    elif episode == 6:
                        if phrase.endswith(',[STARK]\\NLoud and clear.'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1)
                    elif episode == 14:
                        phrase = phrase \
                            .replace('[Fern gasps', '[Fern gasps]')
                    elif episode == 15:
                        if phrase.endswith(',[FRIEREN]\\NMy apologies.'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1)
                    elif episode == 16:
                        phrase = phrase \
                            .replace('[MALE VILLAGER 16C]\\NThat\'s a wild question.', '[STARK]\\NThat\'s a wild question.') \
                            .replace('Oh! You mean\\NMister Gorilla Warrior.', '[MALE VILLAGER 16C]\\NOh! You mean Mister Gorilla Warrior.')
                    elif episode == 21:
                        if phrase.endswith(',Quickly.'):
                            phrase = phrase.replace(',Default,', ',Italics,', 1)
                    elif episode == 22:
                        if phrase.endswith(',[FRIEREN] Glad to see\\Nyou\'re feeling better.'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1)
                    elif episode == 27:
                        if phrase.endswith(',[FRIEREN] Fern.'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1)
                    elif episode == 28:
                        if phrase.endswith(',[FERN] Goodness,\\NMistress Frieren,'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1)
                        elif phrase.endswith(',don\'t look so excited.'):
                            phrase = phrase.replace(',Italics,', ',Default,', 1)
                    out.write(phrase + '\n')
                if episode == 3:
                    out.write('Dialogue: 0,0:05:28.00,0:05:29.79,Top-Alt,Sweet tooth,0,0,0,,After a long day\'s work,\n')
                    out.write('Dialogue: 0,0:05:29.87,0:05:31.46,Top-Alt,Sweet tooth,0,0,0,,there\'s no better reward\\Nthan a plate piled\n')
                    out.write('Dialogue: 0,0:05:31.54,0:05:32.79,Top-Alt,Sweet tooth,0,0,0,,high with ... confections.\n')
                    out.write('Dialogue: 0,0:05:33.25,0:05:35.01,Top-Alt,Sweet tooth,0,0,0,,We\'ll tell you the route, alright?\n')
                insert = False
            if line == '[Events]':
                insert = True


if __name__ == '__main__':
    os.chdir(Path(sys.argv[0]).resolve().parent)
    for i in range(1, 29):
        generate(i)
