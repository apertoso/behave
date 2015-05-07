# -*- coding: utf-8 -*-

from __future__ import absolute_import
import errno
import os
import json
from jinja2 import Environment, FileSystemLoader
from behave.reporter.base import Reporter
from behave.textutil import text as _text
from collections import OrderedDict

class LivingDocMetaDataMenu(object):
    types = ['feature', 'tag', 'tag_page']

    def __init__(self, name, type, expr):
        self.name = name
        if type not in self.types:
            raise StandardError('Incorrect menu type passed')
        self.type = type
        self.expr = expr


class LivingDocMetaDataFeature(object):

    def __init__(self, name, image, links):
        self.name = name
        self.image = image
        self.links = self.process_links(links) if links else None

    @staticmethod
    def process_links(items):
        links = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_url = item['url'] if 'url' in item and item['url'] else None
            link = LivingDocMetaDataLink(item_name, item_url)
            links.append(link)
        return links


class LivingDocMetaDataTag(object):

    def __init__(self, name, image, desc, long_desc, links):
        self.name = name
        self.image = image
        self.desc = desc
        self.long_desc = long_desc
        self.links = self.process_links(links) if links else None

    @staticmethod
    def process_links(items):
        links = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_url = item['url'] if 'url' in item and item['url'] else None
            link = LivingDocMetaDataLink(item_name, item_url)
            links.append(link)
        return links


class LivingDocMetaDataTagPage(object):

    def __init__(self, name, image, desc, links):
        self.name = name
        self.image = image
        self.desc = desc
        self.links = self.process_links(links) if links else None

    @staticmethod
    def process_links(items):
        links = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_url = item['url'] if 'url' in item and item['url'] else None
            link = LivingDocMetaDataLink(item_name, item_url)
            links.append(link)
        return links


class LivingDocMetaDataLink(object):

    def __init__(self, name, url):
        self.name = name
        self.url = url


class LivingDocMetaData(object):

    def __init__(self, config_json):
        """
        Take a JSON string and convert into a meta data object
        """
        if isinstance(config_json, basestring):
            raw_string = config_json
            raw_dict = json.loads(config_json)
            config = raw_dict['config'] if 'config' in raw_dict and \
                                           raw_dict['config'] else None
            self.features = self.process_features(raw_dict['features']) \
                if 'features' in raw_dict and raw_dict['features'] \
                else None
            self.tags = self.process_tags(raw_dict['tags']) if 'tags' in \
                raw_dict and raw_dict['tags'] else None
            if config:
                self.name = config['site_name'] if 'site_name' in \
                    config and config['site_name'] else None
                self.logo = config['logo_url'] if 'logo_url' in \
                    config and config['logo_url'] else None
                self.description = config['site_desc'] if 'site_desc' in \
                    config and config['site_desc'] else None
                self.menu = self.process_menu(config['menu']) if 'menu' \
                    in config and config['menu'] else None
        else:
            raise TypeError('LivingDocMetaData object can only be initiated '
                            'a with string')

    @staticmethod
    def process_menu(items):
        menu_items = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_type = item['type'] if 'type' in item and item['type'] \
                else None
            item_expr = item['expr'] if 'expr' in item and item['expr'] \
                else None
            menu_item = LivingDocMetaDataMenu(item_name, item_type, item_expr)
            menu_items.append(menu_item)
        return menu_items

    @staticmethod
    def process_features(items):
        features = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_image = item['image'] if 'image' in item and item['image'] \
                else None
            item_links = item['links'] if 'links' in item and item['links'] \
                else None
            feature = LivingDocMetaDataFeature(item_name,
                                               item_image,
                                               item_links)
            features.append(feature)
        return features

    @staticmethod
    def process_tags(items):
        tags = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_image = item['image'] if 'image' in item and item['image'] \
                else None
            item_desc = item['desc'] if 'desc' in item and item['desc'] \
                else None
            item_long_desc = item['long_desc'] if 'long_desc' in item and \
                                                  item['long_desc'] else None
            item_links = item['links'] if 'links' in item and item['links'] \
                else None
            tag = LivingDocMetaDataTag(item_name,
                                       item_image,
                                       item_desc,
                                       item_long_desc,
                                       item_links)
            tags.append(tag)
        return tags


class LivingDocReporter(Reporter):
    """
    Generates Living Documentation from Behave.
    """
    jinja_env = Environment(loader=FileSystemLoader('/home/colinwren/dev/'
                                                    'behave/behave/reporter/'
                                                    'templates'))
    feature_links = {}
    tags = {}
    feature_summary = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'untested': 0
    }
    scenario_summary = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'untested': 0
    }
    step_summary = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'undefined': 0,
        'untested': 0
    }

    def __init__(self, config):
        super(LivingDocReporter, self).__init__(config)
        if config.livingdoc_meta:
            with open(config.livingdoc_meta) as data_file:
                config_file = data_file.read()
                self.metadata = LivingDocMetaData(config_file)
        else:
            self.metadata = None

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
        feature_filename = self.make_feature_filename(feature)
        feature_meta = self.metadata['features'] if 'features' in \
                                                    self.metadata else False
        meta = [d for d in feature_meta if d['name'] == feature.name]
        meta = meta[0] if meta else False

        for tag in feature.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(feature)

        # -- BUILD-TESTCASES: From scenarios
        for scenario in feature:
            for tag in scenario.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(scenario)

        if not os.path.exists(self.config.livingdoc_directory):
            # -- ENSURE: Create multiple directory levels at once.
            os.makedirs(self.config.livingdoc_directory)
        feature_dirname = self.config.livingdoc_directory + '/features'
        try:
            os.makedirs(feature_dirname)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(feature_dirname):
                pass
            else:
                raise

        feature_basename = u'%s.html' % feature_filename
        feature_filename = os.path.join(feature_dirname, feature_basename)
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
            'link': feature_basename,
            'desc': meta['desc'] if meta and 'desc' in meta else False,
            'image': meta['image'] if meta and 'image' in meta else False
        })
        feature_html = self.jinja_env.get_template('feature.html')
        with open(feature_filename, 'wb') as f:
            f.write(feature_html.render(feature=feature,
                                        status=status_class,
                                        meta=meta,
                                        path='/features/'+feature_basename,
                                        company_name='LivingDocReporter'))

    def end(self):
        # set up paths

        # set up collections

        #

        src = os.getcwd() + '/behave/reporter/templates/static/'
        dst = self.config.livingdoc_directory + '/static/'
        os.system("cp -R {src} {dst}".format(src=src, dst=dst))
        feature_index_filename = self.config.livingdoc_directory + '/features/' \
                                                                   '_index.html'
        feature_index_html = self.jinja_env.get_template('feature_index.html')
        index_filename = self.config.livingdoc_directory + '/index.html'
        index_html = self.jinja_env.get_template('index.html')
        tag_index_filename = self.config.livingdoc_directory + '/tags/' \
                                                               '_index.html'
        tag_index_html = self.jinja_env.get_template('tag_index.html')
        tag_html = self.jinja_env.get_template('tag.html')
        features_list = OrderedDict(sorted(self.feature_links.items()))
        tags = {}
        tag_meta = self.metadata['tags'] if 'tags' in self.metadata else False
        for tag in self.tags.iteritems():
            tag_name = str(tag[0])
            meta = [d for d in tag_meta if d['name'] == tag_name]
            meta = meta[0] if meta else False
            if tag_name[0] not in tags:
                tags[tag_name[0]] = []
            tag_dict = dict()
            tag_dict['name'] = tag_name
            tag_dict['objs'] = tag[1]
            if meta and 'meta' not in tag_dict:
                tag_dict['meta'] = meta
            tags[tag_name[0]].append(tag_dict)
        tags_list = OrderedDict(sorted(tags.items()))
        stats = [
            {'name': 'Features', 'summary': self.feature_summary},
            {'name': 'Scenarios', 'summary': self.scenario_summary},
            {'name': 'Steps', 'summary': self.step_summary}
        ]

        tag_dirname = self.config.livingdoc_directory + '/tags'
        try:
            os.makedirs(tag_dirname)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(tag_dirname):
                pass
            else:
                raise
        # render a tag file for each tag which will contain
        # the scenarios and features tagged with that tag
        for tag, tags in self.tags.iteritems():
            filename = '{0}/tags/{1}.html'.format(
                self.config.livingdoc_directory, tag)
            with open(filename, 'wb') as f:
                f.write(tag_html.render(title=tag,
                                        tags=tags,
                                        path='/tags/'+tag+'.html'))
        with open(tag_index_filename, 'wb') as f:
            f.write(tag_index_html.render(tags=tags_list))
        with open(feature_index_filename, 'wb') as f:
            f.write(feature_index_html.render(features=features_list))
        with open(index_filename, 'wb') as f:
            f.write(index_html.render(stats=stats,
                                      company_name='LivingDocReporter'))
