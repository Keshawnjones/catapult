# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import StringIO
import unittest

from telemetry import benchmark
from telemetry.command_line import commands
from telemetry import story as story_module
from telemetry import page as page_module
import mock


class BenchmarkFoo(benchmark.Benchmark):
  """Benchmark foo for testing."""

  def page_set(self):
    page = page_module.Page('http://example.com', name='dummy_page',
                            tags=['foo', 'bar'])
    story_set = story_module.StorySet()
    story_set.AddStory(page)
    return story_set

  @classmethod
  def Name(cls):
    return 'BenchmarkFoo'


class BenchmarkDisabled(benchmark.Benchmark):
  """Benchmark disabled for testing."""

  # An empty list means that this benchmark cannot run anywhere.
  SUPPORTED_PLATFORMS = []

  def page_set(self):
    return story_module.StorySet()

  @classmethod
  def Name(cls):
    return 'BenchmarkDisabled'


class PrintBenchmarkListTests(unittest.TestCase):

  def setUp(self):
    self._stream = StringIO.StringIO()
    self._json_stream = StringIO.StringIO()
    self._mock_possible_browser = mock.MagicMock()
    self._mock_possible_browser.browser_type = 'TestBrowser'

  def testPrintBenchmarkListWithNoDisabledBenchmark(self):
    expected_printed_stream = (
        'Available benchmarks for TestBrowser are:\n'
        '  BenchmarkFoo Benchmark foo for testing.\n'
        'Pass --browser to list benchmarks for another browser.\n\n')
    commands.PrintBenchmarkList([BenchmarkFoo],
                                self._mock_possible_browser,
                                self._stream)
    self.assertEquals(expected_printed_stream, self._stream.getvalue())


  def testPrintBenchmarkListWithOneDisabledBenchmark(self):
    expected_printed_stream = (
        'Available benchmarks for TestBrowser are:\n'
        '  BenchmarkFoo      Benchmark foo for testing.\n'
        '\n'
        'Not supported benchmarks for TestBrowser are (force run with -d):\n'
        '  BenchmarkDisabled Benchmark disabled for testing.\n'
        'Pass --browser to list benchmarks for another browser.\n\n')

    with mock.patch.object(
        self._mock_possible_browser, 'GetTypExpectationsTags',
        return_value=['All']):
      commands.PrintBenchmarkList([BenchmarkFoo, BenchmarkDisabled],
                                  self._mock_possible_browser,
                                  self._stream)
      self.assertEquals(expected_printed_stream, self._stream.getvalue())

  def testPrintBenchmarkListInJSON(self):
    expected_json_stream = json.dumps(
        [
            {'name': BenchmarkFoo.Name(),
             'description': BenchmarkFoo.Description(),
             'enabled': True,
             'supported': True,
             'stories': [
                 {
                     'name': 'dummy_page',
                     'tags': [
                         'all',
                         'foo',
                         'bar'
                     ]
                 }
             ]
            }], indent=4, sort_keys=True, separators=(',', ': '))

    commands.PrintBenchmarkList([BenchmarkFoo],
                                self._mock_possible_browser,
                                json_pipe=self._json_stream)
    self.assertEquals(expected_json_stream, self._json_stream.getvalue())
