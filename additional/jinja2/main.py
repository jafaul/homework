from jinja2 import Template, FunctionLoader, Environment, FileSystemLoader
from markupsafe import escape

# jinja2

link = '''
in HTML-doc links are definent so:
<a href="#"> Link <\a>

'''

tm = Template("{{ link | e }}")  # e - екранування
msg = tm.render(link=link)

# or

tm = escape(link)

# for

cities = [
    {'id': 1, 'city': 'Riga'},
    {'id': 5, 'city': 'Kyiv'},
    {'id': 7, 'city': 'Warsaw'},
    {'id': 8, 'city': 'Munich'},
    {'id': 11, 'city': 'Lutsk'}
]
#  # - is cancel \n
link = ''' 
<select name="cities">
{%- for c in cities %}
    {%- if c.id > 6 %}
         <option value="{{ c.id }}">{{ c.city }}</option>
    {%- elif c.city == "Kyiv" %}
        <option value="{{ c.id }}">{{ c.city }}</option>
    {#{%- else %}  #} 
     {# {{ c.city }} #}
    {%- endif %}

{%- endfor %}

</select>

'''

tm = Template(link)
msg = tm.render(cities=cities)
print(msg)

# macro

html = '''
{% macro input(name, value='', type='text', size=20) -%}
    <input type="{{ type }} name="{{ name }}" value="{{ value | e }} size="{{ size }}" 
{%- endmacro %}

<p> {{ input('username') }}
<p> {{ input('email') }}
<p> {{ input('password') }}

'''

tm = Template(html)
msg = tm.render()
print(msg)

persons = [
    {"name": "Alex", "age": 18, "weight": 78.5},
    {"name": "Nick", "age": 28, "weight": 82.3},
    {"name": "John", "age": 33, "weight": 94.0}
]

# caller

html = '''
{% macro list_users(list_of_user) -%}

<ul>
{% for u in list_of_user -%}
    <li> {{ u.name }} {{ caller(u) }}
{%- endfor %}
</ul>

{%- endmacro %}
{% call(user) list_users(users) %}
    <ul>
    <li>age: {{ user.age }}
    <li>weight: {{ user.weight }}
    <ul\>
{% endcall -%}


{#{{ list_users(users) }}#}   {# we don't need this if we use marco with caller #}
'''

tm = Template(html)
msg = tm.render(users=persons)
print(msg)


# func loader

def load_tpl(path):
    if path == "index":
        return "Name {{ u.name }}, age {{ u.age }}"
    else:
        return "Data: {{ u }}"


file_loader = FunctionLoader(load_tpl)
env = Environment(loader=file_loader)
tm = env.get_template('index')
msg = tm.render(u=persons[0])
print(msg)

# include

# {% include ['header.html', 'header2.html'] ignore missing %}
# <p> Page
# {% include 'footer.html' %}

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
tm = env.get_template('page.html')
msg = tm.render(path='/', title='Home')
print(msg)

# template extending

# {% block <block_name> %}
# {% endblock %}
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
tm = env.get_template('about.html')
output = tm.render(list_table=[1, 2, 3, 4])
print(output)

