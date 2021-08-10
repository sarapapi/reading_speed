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

# minimum delay for generating the following sentence for a wait k policy
# consider that wait k policy wait k steps i.e. read k times before writing
# it means that it writes at the k+1 step
DELAY_K = (K+1) * 280

data = [json.loads(line) for line in open(filepath, 'r')]
stats = {'index': [], 'block': [], 'prediction': [], 'start': [], 'end': [], 'duration': [], 'len_char': [], 'read_speed' : []}

# READING SPEED

for i in data:
    pred = i['prediction'].split(' ')
    elapsed = i['elapsed'][:-1]
    source_length = i['source_length']
    assert len(pred) == len(elapsed)
    words = []
    blocktimes = []
    start = elapsed[0]
    init = elapsed[0]
    sent_idx = i['index']
    processed = 0
    repblocks = 0
    for word, time in zip(pred, elapsed):
        words.append(word)
        if word in ['<eol>', '<eob>']:
            if not(len(words) > 2 and words[-2] in ['<eol>', '<eob>']):
                blocktimes.append(time - start)
                start = time
            else:
                words = words[:-1]
                repblocks += 1
                # if a block is predicted after a line, the predicted line is ignored
                # in the block/line division except for the time required to predict it
                if word == '<eob>' and words[-1] == '<eol>':
                    words[-1] = '<eob>'
        # if </s> is encountered, the reading speed is computed
        if len(pred) == len(words) + repblocks:
            blocktimes = blocktimes[1:]
            # if the delay is equal to the length of the segment, it means that the words are
            # generated together, in a single step, when the audio is finished.
            # Since the following prediction will be generated after DELAY_K ms
            # we add this time to the duration in computing the reading speed
            blocktimes.append(DELAY_K)
            blocks = " ".join(words).split('<eob>')
            for nblock, block in enumerate(blocks[:-1]):
                stats['index'].append(sent_idx)
                stats['block'].append(nblock+1)
                stats['prediction'].append(block)
                text = block.replace("<eol>", "")
                ln = len(list(text))
                stats['len_char'].append(ln)
                # Reading speed computation
                lines = block.split('<eol>')
                rspeed = []
                elapsedtime = 0
                elapses = blocktimes[:len(lines)]
                blocktimes = blocktimes[len(lines):]
                for l, t in zip(lines[::-1], elapses[::-1]):
                    elapsedtime += t
                    try:
                        rspeed.append(len(l)*1000/elapsedtime)
                    except ZeroDivisionError:
                        rspeed.append(np.NAN)
                stats['start'].append(init)
                stats['duration'].append(elapsedtime)
                init = init + elapsedtime
                stats['end'].append(init)
                stats['read_speed'].append(max(rspeed))

# add to a dataframe
pd_stats = pd.DataFrame(stats)

# write to csv, subtitle-by-subtitle
with open(filepath.replace(".log", f"_blocks_wait{K}.csv"), 'w') as out:
    pd_stats.to_csv(out)

# DELAY

del_display = []
for i in data:
    pred = i['prediction'].split(' ')
    elapsed = i['elapsed'][:-1]
    delays = i['delays'][:-1]  # ignore the delay for predicting end of sentence
    assert len(pred) == len(elapsed) == len(delays)
    idx_breaks = [0]
    for e, word in enumerate(pred):
        if word == '<eob>':
            idx_breaks.append(e)
    for i, idx in enumerate(idx_breaks):
        start = idx
        try:
            end = idx_breaks[i+1]
        except IndexError:
            break
        emit = elapsed[end]
        for w in range(start, end):
            heard = float(delays[w]) - DELAY_K
            display_delay = emit - heard
            del_display.append(display_delay)

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
