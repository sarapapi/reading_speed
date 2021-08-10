# !/usr/bin/env python3

# Copyright 2021 FBK

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import numpy as np
import pandas as pd
import sys
import statistics

K = int(sys.argv[1])
filepath = sys.argv[2]

MAX_LEN = 84
#K = 5

# minimum delay for generating the following sentence for a wait k policy
# consider that wait k policy wait k steps i.e. read k times before writing
# it means that it writes at the k+1 step
DELAY_K = (K+1) * 280

data = [json.loads(line) for line in open(filepath, 'r')]
stats = {'index': [], 'line': [], 'prediction': [], 'start': [], 'end': [], 'duration': [], 'len_char': [], 'read_speed' : []}

for i in data:
    pred = i['prediction'].split(' ')
    pred.append('</s>')
    elapsed = i['elapsed']  # ignore the delay for predicting end of sentence
    delays = i['delays']
    source_length = i['source_length']
    assert len(pred) == len(elapsed) == len(delays)
    words = []
    elapses = []
    linemax = 0
    start = elapsed[0]
    init = elapsed[0]
    sent_idx = i['index']
    processed = 0
    for word, time, delay in zip(pred, elapsed, delays):
        if word not in ['<eob>', '<eol>']:
            words.append(word)
            elapses.append(time - start)
            # if the MAX_LEN is exceeded or if we are at the end of the segment,
            # we split the sentence and compute the reading speed
            if len(' '.join(words)) > MAX_LEN or word == '</s>':
                stats['index'].append(sent_idx)
                linemax += 1
                stats['line'].append(linemax)
                words = words[:-1]
                text = ' '.join(words)
                stats['prediction'].append(text)
                ln = len(list(text))
                stats['len_char'].append(ln)
                # Max reading speed computation
                if word == '</s>':
                    # if the delay is equal to the length of the segment means that the words are
                    # generated together, in a single step, when the audio is finished.
                    # Since the following prediction will be generated after DELAY_K ms
                    # we add this time to the duration in computing the reading speed
                    elapses[-1] += DELAY_K
                elapsedtime = 0
                if not words:   # handling the case in which only <eob> <eol> is predicted
                    rspeed = [0]
                else:
                    rspeed = []
                    words_tmp = []
                    for word_tmp, elaps in zip(words[::-1], elapses[::-1]):
                        words_tmp.append(word_tmp)
                        text_tmp = ' '.join(words_tmp)
                        elapsedtime += elaps
                        try:
                            rspeed.append(len(text_tmp)*1000/elapsedtime)
                        except ZeroDivisionError:
                            rspeed.append(np.NAN)
                stats['read_speed'].append(max(rspeed))
                stats['duration'].append(elapsedtime)
                stats['start'].append(init)
                init = init + elapsedtime
                stats['end'].append(init)
                start = time
                # initialize the new words accumulator with the word that we cannot insert into the previous sentence
                words = [word]
                elapses = []
            # if the word is not <eob> or <eol> we restart the time counter to the actual time
            start = time

# add to a dataframe
pd_stats = pd.DataFrame(stats)

# write to csv, subtitle-by-subtitle
with open(filepath.replace('.log', f'_scrollingwords_{K}.csv'), 'w') as out:
    pd_stats.to_csv(out)

# DELAY

del_display = []
for i in data:
    del_display.append(i['metric']['latency']['AL'])


# print statistics
print('')
print('- READING SPEED -')
print("Duration (mean and stdev): " + str(round(pd_stats['duration'].mean(), 2)) +
      " +/- " + str(round(pd_stats['duration'].std(), 2)))

print("Reading speed (mean and stdev): " + str(round(pd_stats['read_speed'].mean(), 2)) +
      " +/- " + str(round(pd_stats['read_speed'].std(), 2)))

correct = pd_stats[pd_stats['read_speed'] < 21.01]
print('Percentage of subtitles respecting reading speed (rs < 21.01s): ' +
      str(round(len(correct) / len(pd_stats['read_speed']) * 100, 2)) + '%')

print('')
print('- DELAY -')
print("Subtitle delay: " + str(round(statistics.mean(del_display), 2)) + " +/- " +
      str(round(statistics.stdev(del_display), 2)))
print('')
