# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path
import codecs
import sys, errno, os
from jinja2 import Environment, FileSystemLoader
from xml.etree import ElementTree
from behave.reporter.base import Reporter
from behave.model import Scenario, ScenarioOutline, Step
from behave.formatter import ansi_escapes
from behave.model_describe import ModelDescriptor
from behave.textutil import indent, make_indentation, text as _text
import six
from collections import OrderedDict


def CDATA(text=None):
    # -- issue #70: remove_ansi_escapes(text)
    element = ElementTree.Element('![CDATA[')
    element.text = ansi_escapes.strip_escapes(text)
    return element


class ElementTreeWithCDATA(ElementTree.ElementTree):
    def _write(self, file, node, encoding, namespaces):
        """This method is for ElementTree <= 1.2.6"""

        if node.tag == '![CDATA[':
            text = node.text.encode(encoding)
            file.write("\n<![CDATA[%s]]>\n" % text)
        else:
            ElementTree.ElementTree._write(self, file, node, encoding,
                                           namespaces)

if hasattr(ElementTree, '_serialize'):

    def _serialize_xml2(write, elem, encoding, qnames, namespaces,
                        orig=ElementTree._serialize_xml):
        if elem.tag == '![CDATA[':
            write("\n<%s%s]]>\n" % (elem.tag, elem.text.encode(encoding, "xmlcharrefreplace")))
            return
        return orig(write, elem, encoding, qnames, namespaces)

    def _serialize_xml3(write, elem, qnames, namespaces,
                        short_empty_elements=None,
                        orig=ElementTree._serialize_xml):
        if elem.tag == '![CDATA[':
            write("\n<{tag}{text}]]>\n".format(
                tag=elem.tag, text=elem.text))
            return
        if short_empty_elements:
            # python >=3.3
            return orig(write, elem, qnames, namespaces, short_empty_elements)
        else:
            # python <3.3
            return orig(write, elem, qnames, namespaces)

    if sys.version_info.major == 3:
        ElementTree._serialize_xml = \
            ElementTree._serialize['xml'] = _serialize_xml3
    elif sys.version_info.major == 2:
        ElementTree._serialize_xml = \
            ElementTree._serialize['xml'] = _serialize_xml2


class FeatureReportData(object):
    """
    Provides value object to collect JUnit report data from a Feature.
    """
    def __init__(self, feature, filename, classname=None):
        if not classname and filename:
            classname = filename.replace('/', '.')
        self.feature = feature
        self.filename = filename
        self.classname = classname
        self.testcases = []
        self.counts_tests = 0
        self.counts_errors = 0
        self.counts_failed = 0
        self.counts_skipped = 0

    def reset(self):
        self.testcases = []
        self.counts_tests = 0
        self.counts_errors = 0
        self.counts_failed = 0
        self.counts_skipped = 0


class LivingDocReporter(Reporter):
    """
    Generates Living Documentation from Behave.
    """
    show_multiline = True
    show_timings   = True     # -- Show step timings.
    show_tags      = True
    jinja_env = Environment(loader=FileSystemLoader(os.getcwd()+'/behave/reporter/templates'))
    feature_links = {}
    feature_summary = {'passed': 0, 'failed': 0, 'skipped': 0, 'untested': 0}
    scenario_summary = {'passed': 0, 'failed': 0, 'skipped': 0, 'untested': 0}
    step_summary = {'passed': 0, 'failed': 0, 'skipped': 0, 'undefined': 0, 'untested': 0}

    def make_feature_filename(self, feature):
        filename = None
        for path in self.config.paths:
            if feature.filename.startswith(path):
                filename = feature.filename[len(path) + 1:]
                break
        if not filename:
            # -- NOTE: Directory path (subdirs) are taken into account.
            filename = feature.location.relpath(self.config.base_dir)
        filename = filename.rsplit('.', 1)[0]
        filename = filename.replace('\\', '/').replace('/', '.')
        return _text(filename)

    # -- REPORTER-API:
    def feature(self, feature):
        self.feature_summary[feature.status or 'skipped'] += 1
        feature_filename  = self.make_feature_filename(feature)
        classname = feature_filename
        report = FeatureReportData(feature, feature_filename)

        suite = ElementTree.Element(u'testsuite')
        feature_name = feature.name or feature_filename
        suite.set(u'name', u'%s.%s' % (classname, feature_name))

        # -- BUILD-TESTCASES: From scenarios
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                scenario_outline = scenario
                self._process_scenario_outline(scenario_outline, report)
            else:
                self._process_scenario(scenario, report)

        # -- ADD TESTCASES to testsuite:
        for testcase in report.testcases:
            suite.append(testcase)

        if not os.path.exists(self.config.livingdoc_directory):
            # -- ENSURE: Create multiple directory levels at once.
            os.makedirs(self.config.livingdoc_directory)
        report_dirname = self.config.livingdoc_directory + '/features'
        try:
            os.makedirs(report_dirname)
        except OSError as exc:
            if exc.errno  == errno.EEXIST and os.path.isdir(report_dirname):
                pass
            else:
                raise

        report_basename = u'%s.html' % feature_filename
        report_filename = os.path.join(report_dirname, report_basename)
        status_class = 'btn-warning'
        if feature.status == 'passed':
            status_class = 'btn-success'
        if feature.status == 'failed':
            status_class = 'btn-danger'
        if not feature.name[0] in self.feature_links:
            self.feature_links[feature.name[0]] = []
        self.feature_links[feature.name[0]].append({
            'name': feature.name,
            'status': feature.status,
            'status_class': status_class,
            'file': feature_filename,
            'link': report_basename
        })
        feature_html = self.jinja_env.get_template('feature.html')
        with open(report_filename, 'wb') as f:
            f.write(feature_html.render(feature=feature,
                                        status=status_class,
                                        company_name='LivingDocReporter'))


    def end(self):
        src = os.getcwd() + '/behave/reporter/templates/static/'
        dst = self.config.livingdoc_directory + '/static/'
        os.system("cp -R {src} {dst}".format(src=src, dst=dst))
        feature_index_filename = self.config.livingdoc_directory + '/features/_index.html'
        feature_index_html = self.jinja_env.get_template('feature_index.html')
        index_filename = self.config.livingdoc_directory + '/index.html'
        index_html = self.jinja_env.get_template('index.html')
        features_list = OrderedDict(sorted(self.feature_links.items()))
        stats = [
            {'name': 'Features', 'summary': self.feature_summary},
            {'name': 'Scenarios', 'summary': self.scenario_summary},
            {'name': 'Steps', 'summary': self.step_summary}
        ]
        with open(feature_index_filename, 'wb') as f:
            f.write(feature_index_html.render(features=features_list))
        with open(index_filename, 'wb') as f:
            f.write(index_html.render(stats=stats,
                                      company_name='LivingDocReporter'))


    # -- MORE:
    @staticmethod
    def select_step_with_status(status, steps):
        """
        Helper function to find the first step that has the given step.status.

        EXAMPLE: Search for a failing step in a scenario (all steps).
            >>> scenario = ...
            >>> failed_step = select_step_with_status("failed", scenario)
            >>> failed_step = select_step_with_status("failed", scenario.all_steps)
            >>> assert failed_step.status == "failed"

        EXAMPLE: Search only scenario steps, skip background steps.
            >>> failed_step = select_step_with_status("failed", scenario.steps)

        :param status:  Step status to search for (as string).
        :param steps:   List of steps to search in (or scenario).
        :returns: Step object, if found.
        :returns: None, otherwise.
        """
        for step in steps:
            assert isinstance(step, Step), \
                "TYPE-MISMATCH: step.class=%s"  % step.__class__.__name__
            if step.status == status:
                return step
        # -- OTHERWISE: No step with the given status found.
        # KeyError("Step with status={0} not found".format(status))
        return None

    @classmethod
    def describe_step(cls, step):
        status = _text(step.status)
        if cls.show_timings:
            status += u" in %0.3fs" % step.duration
        text  = u'%s %s ... ' % (step.keyword, step.name)
        text += u'%s\n' % status
        if cls.show_multiline:
            prefix = make_indentation(2)
            if step.text:
                text += ModelDescriptor.describe_docstring(step.text, prefix)
            elif step.table:
                text += ModelDescriptor.describe_table(step.table, prefix)
        return text

    @classmethod
    def describe_tags(cls, tags):
        text = u''
        if tags:
            text = u'@'+ u' @'.join(tags)
        return text

    @classmethod
    def describe_scenario(cls, scenario):
        """
        Describe the scenario and the test status.
        NOTE: table, multiline text is missing in description.

        :param scenario:  Scenario that was tested.
        :return: Textual description of the scenario.
        """
        header_line = u'\n@scenario.begin\n'
        if cls.show_tags and scenario.tags:
            header_line += u'\n  %s\n' % cls.describe_tags(scenario.tags)
        header_line += u'  %s: %s\n' % (scenario.keyword, scenario.name)
        footer_line = u'\n@scenario.end\n' + u'-' * 80 + '\n'
        text = u''
        for step in scenario:
            text += cls.describe_step(step)
        step_indentation = make_indentation(4)
        return header_line + indent(text, step_indentation) + footer_line

    def _process_scenario(self, scenario, report):
        """
        Process a scenario and append information to JUnit report object.
        This corresponds to a JUnit testcase:

          * testcase.@classname = f(filename) +'.'+ feature.name
          * testcase.@name   = scenario.name
          * testcase.@status = scenario.status
          * testcase.@time   = scenario.duration

        Distinguishes now between failures and errors.
        Failures are AssertationErrors: expectation is violated/not met.
        Errors are unexpected RuntimeErrors (all other exceptions).

        If a failure/error occurs, the step, that caused the failure,
        and its location are provided now.

        :param scenario:  Scenario to process.
        :param report:    Context object to store/add info to (outgoing param).
        """
        assert isinstance(scenario, Scenario)
        assert not isinstance(scenario, ScenarioOutline)
        self.scenario_summary[scenario.status or 'skipped'] += 1
        for step in scenario.steps:
            self.step_summary[step.status or 'skipped'] += 1
        report.counts_tests += 1
        classname = report.classname
        feature   = report.feature
        feature_name = feature.name
        if not feature_name:
            feature_name = self.make_feature_filename(feature)

        case = ElementTree.Element('testcase')
        case.set(u'classname', u'%s.%s' % (classname, feature_name))
        case.set(u'name', scenario.name or '')
        case.set(u'status', scenario.status)
        case.set(u'time', _text(round(scenario.duration, 6)))

        step = None
        if scenario.status == 'failed':
            for status in ('failed', 'undefined'):
                step = self.select_step_with_status(status, scenario)
                if step:
                    break
            assert step, "OOPS: No failed step found in scenario: %s" % scenario.name
            assert step.status in ('failed', 'undefined')
            element_name = 'failure'
            if isinstance(step.exception, (AssertionError, type(None))):
                # -- FAILURE: AssertionError
                report.counts_failed += 1
            else:
                # -- UNEXPECTED RUNTIME-ERROR:
                report.counts_errors += 1
                element_name = 'error'
            # -- COMMON-PART:
            failure = ElementTree.Element(element_name)
            step_text = self.describe_step(step).rstrip()
            text = u"\nFailing step: %s\nLocation: %s\n" % (step_text, step.location)
            message = _text(step.exception)
            if len(message) > 80:
                message = message[:80] + "..."
            failure.set(u'type', step.exception.__class__.__name__)
            failure.set(u'message', message)
            text += _text(step.error_message)
            failure.append(CDATA(text))
            case.append(failure)
        elif scenario.status in ('skipped', 'untested'):
            report.counts_skipped += 1
            step = self.select_step_with_status('undefined', scenario)
            if step:
                # -- UNDEFINED-STEP:
                report.counts_failed += 1
                failure = ElementTree.Element(u'failure')
                failure.set(u'type', u'undefined')
                failure.set(u'message', (u'Undefined Step: %s' % step.name))
                case.append(failure)
            else:
                skip = ElementTree.Element(u'skipped')
                case.append(skip)

        # Create stdout section for each test case
        stdout = ElementTree.Element(u'system-out')
        text = self.describe_scenario(scenario)

        # Append the captured standard output
        if scenario.stdout:
            output = _text(scenario.stdout)
            text += u'\nCaptured stdout:\n%s\n' % output
        stdout.append(CDATA(text))
        case.append(stdout)

        # Create stderr section for each test case
        if scenario.stderr:
            stderr = ElementTree.Element(u'system-err')
            output = _text(scenario.stderr)
            text = u'\nCaptured stderr:\n%s\n' % output
            stderr.append(CDATA(text))
            case.append(stderr)

        report.testcases.append(case)

    def _process_scenario_outline(self, scenario_outline, report):
        assert isinstance(scenario_outline, ScenarioOutline)
        for scenario in scenario_outline:
            assert isinstance(scenario, Scenario)
            self._process_scenario(scenario, report)
