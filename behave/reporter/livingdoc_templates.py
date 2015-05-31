__author__ = 'colinwren'

livingdoc_base = """
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Living Documentation for {{ metadata.name }}</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet"/>
    <style type="text/css">

        .panel{
            box-shadow: none;
            -webkit-box-shadow: none;
            margin-bottom: 2em;
        }
        .bdd-hero-outer{
            background-size: cover;
            padding-right: 0;
        }
        .bdd-hero-inner{
            background: linear-gradient(to bottom, rgba(255,255,255,0) 0%,rgba(255,255,255,1) 100%);
            width: calc(100% + 30px);
            padding-top: 200px;
        }


        .panel-title > h3 > small, h2 > small{
            line-height: 2;
        }


        .panel .panel, .background .panel {
            padding-left: 0;
            padding-right: 0;
        }

        @media (min-width: 1200px){
            .bdd-icons{
                width: 12.33333%;
            }
        }


        .bdd-icons > p {
            height: 10em;
        }
        .bdd-icons > p > .icon{
            position: absolute;
            top: 26%;
            left: 35%;
            font-size: 3em;
        }

        .bdd-icons > p > .small-icon{
            position: absolute;
            top: 10%;
            left: 50%;
            font-size: 1.5em;
        }

        .bdd-icons span.icon{
            top: 15%;
        }

        .bdd-icons > p > .icon > .glyphicon-minus:last-child{
            top: -0.8em;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-default" id="top">
        <div class="container">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="#">{{ metadata.name }}</a>
            </div>
            <div class="navbar-collapse collapse" id="navbar">
                <ul class="nav navbar-nav navbar-right">
                    <li><a href="{% block homelevel %}../{% endblock %}index.html">Home</a></li>
                    {% for item in metadata.menu %}
                        <li><a href="{% block navlevel%}../{% endblock %}{{ item.slug }}/index.html">{{ item.name }}</a></li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    <script src="http://code.jquery.com/jquery-1.11.3.min.js" type="text/javascript"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js" type="text/javascript"></script>
    <script type="text/javascript">
        $(document).ready(function(){
            $('.scenario_outline_examples >tbody tr').click(function(){
                var i = null, ec = null, tc = null;
                i = $(this).attr('data-id');
                ec = $(this).parents('.panel-body').find('.examples');
                var e = $(this).parents('.panel').find('#'+ i);
                tc = $(this).parents('.panel').find('.scenario_title');
                var t = $(this).parents('.panel').find('.example_title #title_'+i);
                ec[0].innerHTML = e[0].innerHTML;
                tc[0].innerHTML = t[0].innerHTML;
            });

            $('.panel-heading').click(function(){
               $(this).parents('.panel').find('.panel-body').toggle();
               $(this).parents('.panel').find('.panel-footer').toggle();
            });

            $('img').each(function(){
                $(this).attr('src', $(this).attr('delayedsrc'));
            })
        });
    </script>
</body>
</html>
"""

livingdoc_index = """
{% extends "base.html" %}
{% block content %}
    <h1>{{ site.name }}</h1>
    {{ site.description }}

    <h2>Check out</h2>
    <ul>
        {% for item in site.menu %}
            <li><a href="{{ item.slug }}/index.html">{{ item.name }}</a></li>
        {% endfor %}
    </ul>
{% endblock %}
{% block navlevel %}{% endblock %}
{% block homelevel %}{% endblock %}
"""

livingdoc_directory_index = """
{% extends "base.html" %}
{% block content %}
    {% for item in items %}
        {% if loop.index is odd %}
            <div class="row col-lg-12">
                <div class="col-lg-4">
                    {%  if item.blurb %}{{  item.blurb }}{%  endif %}
                    <p><a href="{{ item.slug }}.html">Read more about {% if item.title %}{{ item.title }}{% else %}{{ item.name }}{% endif %} &gt;</a></p>
                </div>
                <div class="col-lg-offset-2 col-lg-6">
                        {% if item.image %}
                            <img src="#" delayedsrc="{{ item.image }}" class="col-lg-12"/>
                        {%  endif %}
                </div>
                <p>&nbsp;</p>
            </div>
        {% else %}
            <div class="row col-lg-12">
                <div class="col-lg-6">
                        {% if item.image %}
                            <img src="#" delayedsrc="{{ item.image }}" class="col-lg-12"/>
                        {%  endif %}
                </div>
                <div class="col-lg-offset-2 col-lg-4">
                    {%  if item.blurb %}{{  item.blurb }}{%  endif %}
                    <p><a href="{{ item.slug }}.html">Read more about {% if item.title %}{{ item.title }}{% else %}{{ item.name }}{% endif %} &gt;</a></p>
                </div>
                <p>&nbsp;</p>
            </div>
        {% endif %}
        <div class="row col-lg-12">
            <p>&nbsp;</p>
            <p>&nbsp;</p>
        </div>
    {% endfor %}
{% endblock %}
{% block feature_active %} class="active"{% endblock %}
"""

livingdoc_directory_single = """
{% extends "base.html" %}
{% block content %}
 <div class="col-lg-12">
        <ul class="list-inline pull-right">
            {% if item.background %}<li><a href="#background">Background</a></li>{% endif %}
            {% if item.features %}<li><a href="#features">Features</a></li>{% endif %}
            {% if item.scenarios %}<li><a href="#scenarios">Scenarios</a></li>{% endif %}
            {% if item.other_resources %}<li><a href="#other-resources">Other Resources</a></li>{% endif %}
        </ul>
    </div>
<div class="row col-lg-12 bdd-hero-outer" style="background-image: url('{{ item.image }}');">

    <div class="row col-lg-12 bdd-hero-inner">
        <h1>{% if item.title %}{{ item.title }}{% else %}{{ item.name }}{% endif %}</h1>
        {% if item.description %}
        <p class="lead">{% for description in item.description %}{{description}}<br>{% endfor %}</p>
        {% endif %}
    </div>
</div>

<div class="row col-lg-12 background">
    {% if item.background %}
    <h2 id="background">Background <small class="pull-right"><a href="#top">Back to top</a></small></h2>
    <hr>
    {% for step in item.background.steps %}
        {% if step.keyword=='Given' %}
                                <div class="panel panel-warning col-lg-3">
                                    <div class="panel-heading">
                                        <div class="panel-title"><h4>Given</h4></div>
                                    </div>
                                    <ul class="list-group">
                            {% endif %}

                            {% if step.keyword=='When' %}
                                    </ul>
                                </div>
                                <div class="col-lg-1 bdd-icons">
                                    <p>
                                    <i class="glyphicon glyphicon-flash small-icon"></i><br>
                                    <i class="glyphicon glyphicon-user icon"></i></p>
                                </div>
                                <div class="panel panel-info col-lg-3">
                                    <div class="panel-heading">
                                        <div class="panel-title"><h4>When</h4></div>
                                    </div>
                                    <ul class="list-group">
                            {% endif %}

                            {% if step.keyword=='Then' %}
                                    </ul>
                                </div>
                                <div class="col-lg-1 bdd-icons">
                                    <p><span class="icon"><i class="glyphicon glyphicon-minus"></i><br><i class="glyphicon glyphicon-minus"></i></span></p>
                                </div>
                                <div class="panel panel-success col-lg-3">
                                    <div class="panel-heading">
                                        <div class="panel-title"><h4>Then</h4></div>
                                    </div>
                                    <ul class="list-group">
                            {% endif %}


                                    <li class="list-group-item">{% if step.keyword not in ['Given', 'When', 'Then'] %}<strong>{{ step.keyword }}</strong> {%  endif %}{{ step.name }} {% if step.status=='passed' %}<span class="pull-right"><i class="glyphicon glyphicon-ok"></i></span>{% endif %}{% if step.status=='failed' %}<span class="pull-right"><i class="glyphicon glyphicon-remove"></i></span>{% endif %}
                                    {% if step.text %}
                                        <pre>{{ step.text}}</pre>
                                    {% endif %}
                                    {% if step.table %}
                                        <table class="table">
                                            <thead>
                                                <tr>
                                                    {% for heading in step.table.headings %}
                                                        <th>{{ heading }}</th>
                                                    {% endfor %}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for row in step.table.rows %}
                                                    <tr>
                                                       {% for cell in row.cells %}
                                                            <td>{{ cell }}</td>
                                                       {% endfor %}
                                                    </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    {% endif %}
                                    </li>
                        {% endfor %}
                     </ul>
                    </div>
    <p>&nbsp;</p>
    {% endif %}
        </div>
    {% if item.features %}
    <div class="row col-lg-12">
        <h2 id="features">Features <small class="pull-right"><a href="#top">Back to top</a></small></h2>
        <hr>
        <ul>
            {% for feature in item.features %}
                <li><a href="../features/{{ feature.slug }}.html">{{ feature.name }}</a></li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    <div class="row col-lg-12">
    <h2 id="scenarios">Scenarios <small class="pull-right"><a href="#top">Back to top</a></small></h2>
    <hr>
    <!-- <div class="container"> -->
        {% for scenario in item.scenarios %}
            {% if scenario.type=='scenario' %}
                <div class="panel panel-default" id="{{ scenario.slug_id }}">
                    <div class="panel-heading">
                        <div class="panel-title">
                            <h3><span class="text-muted">Scenario:</span> {{ scenario.name }}
                                <small class="pull-right">{% if scenario.tags %}
                                    <span class="text-muted">Tags: </span>
                                    {% for tag in scenario.tags %} <a href="../tags/{{ tag }}.html"><span class="badge btn-info">{{ tag }}</span></a> {% endfor %}
                                    {% endif %}
                                </small>
                            </h3>
                        </div>
                    </div>
                    <div class="panel-body">
                        {% for step in scenario.steps %}
                            {% if step.keyword=='Given' %}
                                <div class="panel panel-warning col-lg-3">
                                    <div class="panel-heading">
                                        <div class="panel-title"><h4>Given</h4></div>
                                    </div>
                                    <ul class="list-group">
                            {% endif %}

                            {% if step.keyword=='When' %}
                                    </ul>
                                </div>
                                <div class="col-lg-1 bdd-icons">
                                    <p>
                                    <i class="glyphicon glyphicon-flash small-icon"></i><br>
                                    <i class="glyphicon glyphicon-user icon"></i></p>
                                </div>
                                <div class="panel panel-info col-lg-3">
                                    <div class="panel-heading">
                                        <div class="panel-title"><h4>When</h4></div>
                                    </div>
                                    <ul class="list-group">
                            {% endif %}

                            {% if step.keyword=='Then' %}
                                    </ul>
                                </div>
                                <div class="col-lg-1 bdd-icons">
                                    <p><span class="icon"><i class="glyphicon glyphicon-minus"></i><br><i class="glyphicon glyphicon-minus"></i></span></p>
                                </div>
                                <div class="panel panel-success col-lg-3">
                                    <div class="panel-heading">
                                        <div class="panel-title"><h4>Then</h4></div>
                                    </div>
                                    <ul class="list-group">
                            {% endif %}


                                    <li class="list-group-item">{% if step.keyword not in ['Given', 'When', 'Then'] %}<strong>{{ step.keyword }}</strong> {%  endif %}{{ step.name }} {% if step.status=='passed' %}<span class="pull-right"><i class="glyphicon glyphicon-ok"></i></span>{% endif %}{% if step.status=='failed' %}<span class="pull-right"><i class="glyphicon glyphicon-remove"></i></span>{% endif %}
                                    {% if step.text %}
                                        <pre>{{ step.text}}</pre>
                                    {% endif %}
                                    {% if step.table %}
                                        <table class="table">
                                            <thead>
                                                <tr>
                                                    {% for heading in step.table.headings %}
                                                        <th>{{ heading }}</th>
                                                    {% endfor %}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for row in step.table.rows %}
                                                    <tr>
                                                       {% for cell in row.cells %}
                                                            <td>{{ cell }}</td>
                                                       {% endfor %}
                                                    </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    {% endif %}
                                    </li>

                        {% endfor %}
                                </ul>
                             </div>
                        <p>&nbsp;</p>
                        <p><span class="pull-right"><a href="../features/{{ scenario.slug }}" class="btn">Link to scenario</a></span></p>
                    </div>
                </div>
                <p>&nbsp;</p>
            {% endif %}
            {% if scenario.type=='scenario_outline' %}
                <div class="panel panel-default" id="{{ scenario.slug_id }}">
                    <div class="panel-heading">
                        <div class="panel-title">
                            <h3><span class="text-muted">Scenario Outline:</span> <span class="scenario_title">{{ scenario.name | e }}</span> <span class="pull-right">{% if scenario.tags %}<span class="text-muted">Tags: </span>{% for tag in scenario.tags %} <a href="../tags/{{ tag }}.html"><span class="badge btn-info">{{ tag }}</span></a> {% endfor %}  {% endif %}</span></h3>
                        </div>
                    </div>
                    <div class="panel-body" id="{{ loop.index }}_content">
                        <div class="{{ loop.index }}_example examples">
                            {% for step in scenario.steps %}
                                {% if step.keyword=='Given' %}
                                    <div class="panel panel-warning col-lg-3">
                                        <div class="panel-heading">
                                            <div class="panel-title"><h4>Given</h4></div>
                                        </div>
                                        <ul class="list-group">
                                {% endif %}

                                {% if step.keyword=='When' %}
                                        </ul>
                                    </div>
                                    <div class="col-lg-1 bdd-icons">
                                        <p>
                                        <i class="glyphicon glyphicon-flash small-icon"></i><br>
                                        <i class="glyphicon glyphicon-user icon"></i></p>
                                    </div>
                                    <div class="panel panel-info col-lg-3">
                                        <div class="panel-heading">
                                            <div class="panel-title"><h4>When</h4></div>
                                        </div>
                                        <ul class="list-group">
                                {% endif %}

                                {% if step.keyword=='Then' %}
                                        </ul>
                                    </div>
                                    <div class="col-lg-1 bdd-icons">
                                        <p><span class="icon"><i class="glyphicon glyphicon-minus"></i><br><i class="glyphicon glyphicon-minus"></i></span></p>
                                    </div>
                                    <div class="panel panel-success col-lg-3">
                                        <div class="panel-heading">
                                            <div class="panel-title"><h4>Then</h4></div>
                                        </div>
                                        <ul class="list-group">
                                {% endif %}
                                            <li class="list-group-item">{% if step.keyword not in ['Given', 'When', 'Then'] %}<strong>{{ step.keyword }}</strong> {%  endif %}{{ step.name | e }} {% if step.status=='passed' %}<span class="pull-right"><i class="glyphicon glyphicon-ok"></i></span>{% endif %}{% if step.status=='failed' %}<span class="pull-right"><i class="glyphicon glyphicon-remove"></i></span>{% endif %}</li>
                                        </ul>
                                        {% if step.table %}
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    {% for heading in step.table.headings %}
                                                        <th>{{ heading | e }}</th>
                                                    {% endfor %}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for row in step.table.rows %}
                                                    <tr>
                                                       {% for cell in row.cells %}
                                                            <td>{{ cell | e }}</td>
                                                       {% endfor %}
                                                    </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    {% endif %}
                            {% endfor %}
                            </div>
                        </div>
                        {% if scenario.examples %}
                            <div class="container-fluid" id="{{ loop.index }}_examples">
                            {% for example in scenario.examples %}
                                <h3>Examples <small class="pull-right">Click on a row to change scenario text</small></h3>
                                <table class="table scenario_outline_examples table-hover">
                                    <thead>
                                        <tr>
                                            {% for header in example.table.headings %}
                                                <th>{{ header }}</th>
                                            {% endfor %}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for row in example.table.rows %}
                                            <tr data-id="example_{{ row.id | replace('.', '_') }}">
                                                {% for cell in row.cells %}
                                                    <th>{{ cell }}</th>
                                                {% endfor %}
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            {% endfor %}
                            </div>
                        {% endif %}
                        <div class="hidden example_content">
                            {% for scen in scenario.scenarios %}
                                <div class="container-fluid" id="example_{{ scen._row.id | replace('.', '_') }}">
                                {% for step in scen.steps %}
                                    {% if step.keyword=='Given' %}
                                    <div class="panel panel-warning col-lg-3">
                                        <div class="panel-heading">
                                            <div class="panel-title"><h4>Given</h4></div>
                                        </div>
                                        <ul class="list-group">
                                    {% endif %}

                                    {% if step.keyword=='When' %}
                                            </ul>
                                        </div>
                                        <div class="col-lg-1 bdd-icons">
                                            <p>
                                            <i class="glyphicon glyphicon-flash small-icon"></i><br>
                                            <i class="glyphicon glyphicon-user icon"></i></p>
                                        </div>
                                        <div class="panel panel-info col-lg-3">
                                            <div class="panel-heading">
                                                <div class="panel-title"><h4>When</h4></div>
                                            </div>
                                            <ul class="list-group">
                                    {% endif %}

                                    {% if step.keyword=='Then' %}
                                            </ul>
                                        </div>
                                        <div class="col-lg-1 bdd-icons">
                                            <p><span class="icon"><i class="glyphicon glyphicon-minus"></i><br><i class="glyphicon glyphicon-minus"></i></span></p>
                                        </div>
                                        <div class="panel panel-success col-lg-3">
                                            <div class="panel-heading">
                                                <div class="panel-title"><h4>Then</h4></div>
                                            </div>
                                            <ul class="list-group">
                                    {% endif %}
                                            <li class="list-group-item">{% if step.keyword not in ['Given', 'When', 'Then'] %}<strong>{{ step.keyword }}</strong> {%  endif %}{{ step.name | e }} {% if step.status=='passed' %}<span class="pull-right"><i class="glyphicon glyphicon-ok"></i></span>{% endif %}{% if step.status=='failed' %}<span class="pull-right"><i class="glyphicon glyphicon-remove"></i></span>{% endif %}</li>
                                        </ul>
                                        {% if step.table %}
                                        <table class="table table-hover">
                                            <thead>
                                                <tr>
                                                    {% for heading in step.table.headings %}
                                                        <th>{{ heading | e }}</th>
                                                    {% endfor %}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for row in step.table.rows %}
                                                    <tr>
                                                       {% for cell in row.cells %}
                                                            <td>{{ cell | e }}</td>
                                                       {% endfor %}
                                                    </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    {% endif %}
                                {% endfor %}
                                </div>
                                </div>
                            {% endfor %}
                        </div>
                        <div class="hidden example_title">
                            {% for scen in scenario.scenarios %}
                                <span id="title_example_{{ scen._row.id | replace('.', '_') }}">{{ scen.name }}</span>
                            {% endfor %}
                        </div>
                        <p>&nbsp;</p>
                        <p><span class="pull-right"><a href="../features/{{ scenario.slug }}" class="btn">Link to scenario</a></span></p>
                    </div>
                </div>
                <p>&nbsp;</p>
            {% endif %}
        {% endfor %}
        </div>
    {%  if item.other_resources %}
        <div class="row col-lg-12">

        <h2 id="other-resources">Other Resources <small class="pull-right"><a href="#top">Back to top</a></small></h2>
        <hr>
        <ul>

        {% for entry in item.other_resources %}
            <li><a href="{{ entry.url }}">{{ entry.name }}</a></li>
        {% endfor %}
        </ul>
        <p>&nbsp;</p>
        </div>
    {%  endif %}
{% endblock %}
{% block feature_active %} class="active"{% endblock %}
"""

livingdoc_single_page = """
{% extends "base.html" %}
{% block content %}
<div class="row">
    <h2>{{ title }}</h2>
    {% for item in items %}
        {% if loop.index is odd %}
            <div class="row col-lg-12">
                <div class="col-lg-4">
                    <h3>{% if item.title %}{{ item.title }}{% else %}{{ item.name }}{% endif %}</h3>
                    {%  if item.blurb %}{{ item.blurb }}{%  endif %}
                    {%  if item.features %}
                    <h4>Features</h4>
                    <ul>
                        {% for feature in item.features %}
                            <li><a href="../features/{{ feature.slug }}.html">{{ feature.name }}</a></li>
                        {% endfor %}
                    </ul>
                    {%  endif %}
                    {%  if item.scenarios %}
                    <h4>Scenarios</h4>
                    <ul>
                        {% for scenario in item.scenarios %}
                            <li><a href="../features/{{ scenario.slug }}">{{ scenario.name }}</a></li>
                        {% endfor %}
                    </ul>
                    {%  endif %}
                </div>
                <div class="col-lg-offset-2 col-lg-6">
                        {% if item.image %}
                            <img src="#" delayedsrc="{{ item.image }}" class="col-lg-12"/>
                        {%  endif %}
                </div>
                <p>&nbsp;</p>
            </div>
        {% else %}
            <div class="row col-lg-12">
                <div class="col-lg-6">
                        {% if item.image %}
                            <img src="#" delayedsrc="{{ item.image }}" class="col-lg-12"/>
                        {%  endif %}
                </div>
                <div class="col-lg-offset-2 col-lg-4">
                    <h3>{% if item.title %}{{ item.title }}{% else %}{{ item.name }}{% endif %}</h3>
                    {%  if item.blurb %}{{ item.blurb }}{%  endif %}
                    {%  if item.features %}
                    <h4>Features</h4>
                    <ul>
                        {% for feature in item.features %}
                            <li><a href="../features/{{ feature.slug }}.html">{{ feature.name }}</a></li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    {%  if item.scenarios %}
                    <h4>Scenarios</h4>
                    <ul>
                        {% for scenario in item.scenarios %}
                            <li><a href="../features/{{ scenario.slug }}">{{ scenario.name }}</a></li>
                        {% endfor %}
                    </ul>
                    {%  endif %}
                </div>
                <p>&nbsp;</p>
            </div>
        {% endif %}
        <div class="row col-lg-12">
            <p>&nbsp;</p>
            <p>&nbsp;</p>
        </div>
    {% endfor %}
</div>
{% endblock %}
{% block tag_active %} class="active"{% endblock %}
"""