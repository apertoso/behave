# -*- coding: utf-8 -*-

from __future__ import absolute_import
import errno
import os
import json
from jinja2 import Environment, FileSystemLoader
from behave.reporter.base import Reporter
from collections import OrderedDict


def slugify_string(string_to_slug):
    char_to_remove = '-&()~`!@£$%^&*(){}[]:;"\'\\|<>,./?¹€#¼½¾{[]}─·'
    for character in char_to_remove:
        string_to_slug = string_to_slug.replace(character.decode('ascii',
                                                                 'ignore'),
                                                '')
    return '-'.join(string_to_slug.lower().split(' '))


def process_links(items):
        links = []
        for item in items:
            item_name = item['name'] if 'name' in item and item['name'] \
                else None
            item_url = item['url'] if 'url' in item and item['url'] else None
            link = LivingDocMetaDataLink(item_name, item_url)
            links.append(link)
        return links


class LivingDocMetaDataMenu(object):
    _types = ['feature', 'tag', 'tag_page']

    def __init__(self, name, menu_type, expr):
        self.name = name
        if menu_type not in self._types:
            raise StandardError('Incorrect menu type passed')
        self.type = menu_type
        self.expr = expr


class LivingDocMetaDataFeature(object):

    def __init__(self, name, image, desc, links):
        self.name = name
        self.image = image
        self.desc = desc
        self.links = process_links(links) if links else None


class LivingDocMetaDataTag(object):

    def __init__(self, name, image, desc, long_desc, links):
        self.name = name
        self.image = image
        self.desc = desc
        self.long_desc = long_desc
        self.links = process_links(links) if links else None


class LivingDocMetaDataTagPage(object):

    def __init__(self, name, image, desc, links):
        self.name = name
        self.image = image
        self.desc = desc
        self.links = process_links(links) if links else None


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
            item_desc = item['desc'] if 'desc' in item and item['desc'] \
                else None
            item_links = item['links'] if 'links' in item and item['links'] \
                else None
            feature = LivingDocMetaDataFeature(item_name,
                                               item_image,
                                               item_desc,
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


class LivingDocFeature(object):

    def __init__(self, feature, metadata):
        self.__dict__ = feature.__dict__.copy()
        if len(metadata) > 0:
            meta = metadata[0]
            self.image = meta.image
            self.other_resources = meta.links
            self.blurb = meta.desc
            self.slug = slugify_string(self.name)
        else:
            self.image = None
            self.other_resources = None
            self.blurb = None
            self.slug = slugify_string(self.name)


class LivingDocTag(object):

    def __init__(self, tag, metadata):
        self.name = tag
        self.features = []
        self.scenarios = []
        if len(metadata) > 0:
            meta = metadata[0]
            self.name = meta.name
            self.image = meta.image
            self.blurb = meta.desc
            self.desc = meta.long_desc
            self.other_resources = meta.links
        else:
            self.name = None
            self.image = None
            self.blurb = None
            self.desc = None
            self.other_resource = None
        self.slug = slugify_string(self.name)


class LivingDocReporter(Reporter):
    """
    Generates Living Documentation from Behave.
    """

    def __init__(self, config):
        super(LivingDocReporter, self).__init__(config)
        # setup jinja env
        self.jinja_env = Environment(loader=FileSystemLoader(
            '/home/colinwren/dev/behave/behave/reporter/templates'))

        # setup array for features
        self.features = []

        # setup meta data object
        if config.livingdoc_meta:
            with open(config.livingdoc_meta) as data_file:
                config_file = data_file.read()
                self.metadata = LivingDocMetaData(config_file)
        else:
            self.metadata = None

        # setup output directory
        if not os.path.exists(self.config.livingdoc_directory):
            os.makedirs(self.config.livingdoc_directory)

        # create folder for each menu item
        menu_dirs = [slugify_string(menu.name) for menu in self.metadata.menu] \
            if self.metadata and self.metadata.menu else ['features']
        menu_dirs.append(u'static')
        for menu_dir in menu_dirs:
            output_path = '{0}/{1}/'.format(self.config.livingdoc_directory,
                                            menu_dir)
            try:
                os.makedirs(output_path)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(output_path):
                    pass
                else:
                    raise

        # move static files into place
        # TODO: change to be relative to behave library / pass own templates
        src = '/home/colinwren/dev/behave/behave/reporter/templates/static/'
        dst = self.config.livingdoc_directory + '/static/'
        try:
            os.system("cp -R {src} {dst}".format(src=src, dst=dst))
        except OSError:
            raise

    def feature(self, feature):
        meta = [metadata for metadata in self.metadata.features if
                metadata.name == feature.name]
        living_doc_feature = LivingDocFeature(feature, meta)
        self.features.append(living_doc_feature)

    def end(self):
        index_html = self.jinja_env.get_template('index.html')
        tag_index_html = self.jinja_env.get_template('tag_index.html')
        tag_html = self.jinja_env.get_template('tag.html')

        # iterate through menu stuff
        menu_items = self.metadata.menu if self.metadata and \
            self.metadata.menu else [LivingDocMetaDataMenu('Features',
                                                           'feature', None)]

        for menu_item in menu_items:
            if menu_item.type == 'feature':
                self.render_features(menu_item)
            elif menu_item.type == 'tag':
                print 1
            # elif menu_item.type == 'tag_page':



        #     f.write(feature_html.render(feature=feature,
        #                                 status=status_class,
        #                                 meta=meta,
        #                                 path='/features/'+feature_basename,
        #                                 company_name='LivingDocReporter'))

        # features_list = OrderedDict(sorted(self.feature_links.items()))
        # tags = {}
        # tag_meta = self.metadata['tags'] if 'tags' in self.metadata else False
        # for tag in self.tags.iteritems():
        #     tag_name = str(tag[0])
        #     meta = [d for d in tag_meta if d['name'] == tag_name]
        #     meta = meta[0] if meta else False
        #     if tag_name[0] not in tags:
        #         tags[tag_name[0]] = []
        #     tag_dict = dict()
        #     tag_dict['name'] = tag_name
        #     tag_dict['objs'] = tag[1]
        #     if meta and 'meta' not in tag_dict:
        #         tag_dict['meta'] = meta
        #     tags[tag_name[0]].append(tag_dict)
        # tags_list = OrderedDict(sorted(tags.items()))
        # stats = [
        #     {'name': 'Features', 'summary': self.feature_summary},
        #     {'name': 'Scenarios', 'summary': self.scenario_summary},
        #     {'name': 'Steps', 'summary': self.step_summary}
        # ]
        #
        # tag_dirname = self.config.livingdoc_directory + '/tags'
        # try:
        #     os.makedirs(tag_dirname)
        # except OSError as exc:
        #     if exc.errno == errno.EEXIST and os.path.isdir(tag_dirname):
        #         pass
        #     else:
        #         raise
        # # render a tag file for each tag which will contain
        # # the scenarios and features tagged with that tag
        # for tag, tags in self.tags.iteritems():
        #     filename = '{0}/tags/{1}.html'.format(
        #         self.config.livingdoc_directory, tag)
        #     with open(filename, 'wb') as f:
        #         f.write(tag_html.render(title=tag,
        #                                 tags=tags,
        #                                 path='/tags/'+tag+'.html'))
        # with open(tag_index_filename, 'wb') as f:
        #     f.write(tag_index_html.render(tags=tags_list))
        # with open(feature_index_filename, 'wb') as f:
        #     f.write(feature_index_html.render(features=features_list))
        # with open(index_filename, 'wb') as f:
        #     f.write(index_html.render(stats=stats,
        #                               company_name='LivingDocReporter'))


    def render_features(self, menu_item):
        index_html = self.jinja_env.get_template('feature_index.html')
        single_html = self.jinja_env.get_template('feature.html')
        output_dir = '{0}/{1}/'.format(self.config.livingdoc_directory,
                                        slugify_string(menu_item.name))
        index_filename = '{0}index.html'.format(output_dir)
        index_render = index_html.render(features=self.features,
                                         metadata=self.metadata)
        with open(index_filename, 'wb') as f:
            f.write(index_render)
        for feature in self.features:
            feature_render = single_html.render(feature=feature,
                                                metadata=self.metadata)
            feature_filename = '{0}{1}.html'.format(output_dir, feature.slug)
            with open(feature_filename, 'wb') as f:
                f.write(feature_render)

