#!/usr/bin/env python
##  Copyright (c) 2012 The WebM project authors. All Rights Reserved.
##
##  Use of this source code is governed by a BSD-style license
##  that can be found in the LICENSE file in the root of the source
##  tree. An additional intellectual property rights grant can be found
##  in the file PATENTS.  All contributing project authors may
##  be found in the AUTHORS file in the root of the source tree.
##

## This file contains our necessary database definitions

# Setup django to silence deprecation warning for 0.96
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import db
from cache import CachedDataView, GlobalDataView
import datetime
import pickle

class DataUploadLog(db.Model):
    user = db.UserProperty()
    time = db.DateTimeProperty(auto_now_add=True)
    path = db.StringProperty()
    data = db.TextProperty()

class Metric(db.Model):
    # key_name is the metric name (a less pretty version of display name)
    display_name = db.StringProperty()
    distortion = db.BooleanProperty()
    yaxis = db.StringProperty()

class MetricCache(CachedDataView):
    def begin_getitems(self, metricnames):
        keys = [db.Key.from_path('Metric', x) for x in metricnames]
        return db.get_async(keys)

    @classmethod
    def all_keys(cls):
        return [k.name() for k in Metric.all(keys_only = True)]

metrics = GlobalDataView(MetricCache)

class File(db.Model):
    # key_name is the filename
    display_name = db.StringProperty()
    file_sets = db.StringListProperty()

class FileCache(CachedDataView):
    def begin_getitems(self, filenames):
        keys = [db.Key.from_path('File', x) for x in filenames]
        return db.get_async(keys)

    @classmethod
    def all_keys(cls):
        return [k.name() for k in File.all(keys_only = True)]

files = GlobalDataView(FileCache)

class FileSet(db.Model):
    # key_name is the file set name
    display_name = db.StringProperty()
    files = db.StringListProperty()

class FileSetCache(CachedDataView):
    def begin_getitems(self, filesets):
        keys = [db.Key.from_path('FileSet', x) for x in filesets]
        return db.get_async(keys)

    @classmethod
    def all_keys(cls):
        return [k.name() for k in FileSet.all(keys_only = True)]

filesets = GlobalDataView(FileSetCache)

class Commit(db.Model):
    author = db.StringProperty()
    author_time = db.DateTimeProperty()
    committer = db.StringProperty()
    commit_time = db.DateTimeProperty()
    message = db.TextProperty()
    branches = db.StringListProperty()
    parents = db.StringListProperty()
    depth = db.IntegerProperty()
    gerrit_change_id = db.StringProperty()
    gerrit_change_num = db.IntegerProperty()
    gerrit_url = db.StringProperty()
    gerrit_branch = db.StringProperty()
    gerrit_patchset_num = db.IntegerProperty()
    gerrit_patchset_ref = db.StringProperty()

class CommitCache(CachedDataView):
    def begin_getitems(self, commits):
        keys = [db.Key.from_path('Commit', commit) for commit in commits]
        return db.get_async(keys)

    def begin_getitem(self, commit):
        key = db.Key.from_path('Commit', commit)
        return db.get_async(key)

    @classmethod
    def all_keys(cls):
        return [k.name() for k in Commit.all(keys_only = True)]

commits = GlobalDataView(CommitCache)

class DictProperty(db.Property):
  data_type = dict

  def get_value_for_datastore(self, model_instance):
    value = super(DictProperty, self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(value))

  def make_value_from_datastore(self, value):
    if value is None:
      return dict()
    return pickle.loads(value)

  def default_value(self):
    if self.default is None:
      return dict()
    else:
      return super(DictProperty, self).default_value().copy()

  def validate(self, value):
    if not isinstance(value, dict):
      raise db.BadValueError('Property %s needs to be convertible '
                             'to a dict instance (%s) of class dict' % (self.name, value))
    return super(DictProperty, self).validate(value)

  def empty(self, value):
    return value is None


class CodecMetric(db.Model):
    commit = db.StringProperty()
    config_flags = db.StringProperty()
    runtime_flags = db.StringProperty()
    config_name = db.StringProperty()
    data = DictProperty()

class CodecMetricTimeSeries(db.Model):
    metric = db.StringProperty()
    config_name = db.StringProperty()
    file_or_set_name = db.StringProperty()
    branch = db.StringProperty()
    commits = db.StringListProperty()
    times = db.ListProperty(datetime.datetime)
    values = db.ListProperty(float)

class CodecMetricIndex(db.Model):
    # parent = CodecMetric
    commit = db.StringProperty()
    config_name = db.StringProperty()
    files = db.StringListProperty()
    metrics = db.StringListProperty()
