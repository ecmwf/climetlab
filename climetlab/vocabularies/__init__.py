#!/usr/bin/env python
#
# (C) Copyright 2021- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#
import logging
from collections import defaultdict

import editdistance

LOG = logging.getLogger(__name__)

MAPPING = defaultdict(set)

VOCABULARIES = {}


class Vocabulary:
    def __init__(self, name):
        self.name = name
        self.words = {}

    def add(self, word, key=None):
        self.words[word] = key
        if key is not None:
            MAPPING[word].add((self.name, key))

    def normalise(self, word):
        if word in self.words:
            return word

        distance, best = min((editdistance.eval(word, w), w) for w in self.words.keys())
        # if distance < min(len(word), len(best)):
        LOG.warning(
                "Cannot find '%s' in %s vocabulary, did you mean '%s'?",
                word,
                self.name,
                best,
            )

        return word


mars = Vocabulary("mars")
mars.add("2t", 1)
mars.add("tp", 2)
mars.add("ci", 3)
VOCABULARIES["mars"] = mars

cf = Vocabulary("cf")
cf.add("t2m", 1)
cf.add("tp", 2)
cf.add("siconc", 3)
VOCABULARIES["cf"] = cf
