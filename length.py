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
import re
import sys

infile = sys.argv[1]
data = [json.loads(line) for line in open(infile, 'r')]

correct = 0
too_long = []
too_short = []
total_subs = 0
for i in data:
    pred = i['prediction']
    ref = i['reference']
    subs = re.split(r' <eob>| <eol>', pred)
    for sub in subs:
        if sub != '':
            total_subs += 1
            length = len(list(sub.lstrip()))
            if length > 42:
                too_long.append(length - 42)
            elif length < 6:
                too_short.append(length)
            else:
                correct += 1

print('- CONFORMITY -')
print('Correct length: ' + str(correct) + ' (' + str(round(correct/total_subs*100, 2)) + '%)')
print('Too_long (> 43): ' + str(len(too_long)) + ' (' 
      + str(round(len(too_long)/total_subs*100, 2)) +
      '%) - Average length: ' + str(round(sum(too_long) / len(too_long), 2)))
print('Too_short (< 6): ' + str(len(too_short)) + ' ('
      + str(round(len(too_short)/total_subs*100, 2)) +
      '%) - Average length: ' + str(round(sum(too_short) / len(too_short), 2)))
