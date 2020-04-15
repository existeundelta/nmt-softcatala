#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2020 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from __future__ import print_function
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import json
import datetime
from opennmt import OpenNMT
import pyonmttok
from threading import Thread
import re

app = Flask(__name__)
CORS(app)

openNMT_engcat = OpenNMT()
openNMT_engcat.tokenizer_source = pyonmttok.Tokenizer(mode="none", sp_model_path="en_m.model")
openNMT_engcat.tokenizer_target = pyonmttok.Tokenizer(mode="none", sp_model_path="ca_m.model")

openNMT_engcat1 = OpenNMT()
openNMT_engcat1.tokenizer_source = pyonmttok.Tokenizer(mode="none", sp_model_path="en_m.model")
openNMT_engcat1.tokenizer_target = pyonmttok.Tokenizer(mode="none", sp_model_path="ca_m.model")

openNMT_engcat2 = OpenNMT()
openNMT_engcat2.tokenizer_source = pyonmttok.Tokenizer(mode="none", sp_model_path="en_m.model")
openNMT_engcat2.tokenizer_target = pyonmttok.Tokenizer(mode="none", sp_model_path="ca_m.model")

openNMT_engcat3 = OpenNMT()
openNMT_engcat3.tokenizer_source = pyonmttok.Tokenizer(mode="none", sp_model_path="en_m.model")
openNMT_engcat3.tokenizer_target = pyonmttok.Tokenizer(mode="none", sp_model_path="ca_m.model")

openNMT_engcat4 = OpenNMT()
openNMT_engcat4.tokenizer_source = pyonmttok.Tokenizer(mode="none", sp_model_path="en_m.model")
openNMT_engcat4.tokenizer_target = pyonmttok.Tokenizer(mode="none", sp_model_path="ca_m.model")


openNMT_cateng = OpenNMT()
openNMT_cateng.tokenizer_source = pyonmttok.Tokenizer(mode="none", sp_model_path="ca_m.model")
openNMT_cateng.tokenizer_target = pyonmttok.Tokenizer(mode="none", sp_model_path="en_m.model")

@app.route('/translate_old/', methods=['GET'])
def translate_old_api():
    start_time = datetime.datetime.now()
    text = request.args.get('text')
    languages = request.args.get('languages')

    if languages == 'eng-cat':
        model_name = 'eng-cat'
        openNMT = openNMT_engcat
    else:
        model_name = 'cat-eng'
        openNMT = openNMT_cateng

    translated = openNMT.translate(model_name, text)
    result = {}
    result['text'] = text
    result['translated'] = translated
    result['time'] = str(datetime.datetime.now() - start_time)
    return json_answer(json.dumps(result, indent=4, separators=(',', ': ')))

def translate_thread(sentence, openNMT, i, model_name, results):
    if sentence.strip() == '':
        results[i] = ''
    else:
        results[i] = openNMT.translate(model_name, sentence)
#    print("{0} - {1} -> {2}".format(i, sentence, results[i]))

def split_string(sentence):
    strings = []
    translate = []
    start = 0
    pos = 1

    for i in range(0, len(sentence)):
        pos = i
        c = sentence[i]
        if c == '.':
            string = sentence[start:i+1]
            strings.append(string)
            translate.append(True)
            start = i + 1

        if c == '\n' or c == '\r':
            if start < i:
                string = sentence[start:i+1]
                strings.append(string)
                translate.append(True)
             
            string = sentence[i]
            strings.append(string)
            translate.append(False)
            start = i + 1
 
    if start < pos:
        string = sentence[start:pos+1]
        strings.append(string)
        translate.append(True)
    
#    for i in range(0, len(strings)):
#        print("{0}->'{1}':{2}".format(i, strings[i], translate[i]))

    return strings, translate

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route('/translate/', methods=['POST'])
def translate_api():
    start_time = datetime.datetime.now()
    text = request.json['text']
    languages = request.json['languages']

    if languages == 'eng-cat':
        model_name = 'eng-cat'
        openNMT = openNMT_engcat
    else:
        model_name = 'cat-eng'
        openNMT = openNMT_cateng

#    print("Input:" + text)
    sentences, translate = split_string(text)

    num_sentences = len(sentences)
    num_threads = 0
    for i in range(0, len(sentences)):
#        print("Sentence: '{0}': {1}".format(sentences[i], translate[i]))
        if translate[i] is False:
            continue
       
        num_threads = num_threads + 1

    threads = []
    results = ["" for x in range(num_sentences)]
    for i in range(num_sentences):
        if translate[i] is False:
            continue
        
        process = Thread(target=translate_thread, args=[sentences[i], openNMT, i, model_name, results])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

#    print("All threads processed")

    translated = ''
    for i in range(0, num_sentences):
        if translate[i] is True:
            translated += results[i] + " "
        else:
            translated += sentences[i]

#    print("Translated:" + str(translated))
    result = {}
    result['text'] = text
    result['translated'] = translated
    result['time'] = str(datetime.datetime.now() - start_time)
    return json_answer(json.dumps(result, indent=4, separators=(',', ': ')))


@app.route('/version/', methods=['GET'])
def version_api():

    with open("model-description-engcat.txt", "r") as th_description:
        lines = th_description.read().splitlines()

    with open("model-description-cateng.txt", "r") as th_description:
        lines_cat_eng = th_description.read().splitlines()

    lines += lines_cat_eng

    result = {}
    result['version'] = lines
    return json_answer(json.dumps(result, indent=4, separators=(',', ': ')))


def json_answer(data):
    resp = Response(data, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    app.debug = True
    app.run()
