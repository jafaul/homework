<!DOCTYPE html>

<html lang="en_US">
<head> 
	<title> {% block title %}{% endblock %} </title>
</head>
<body>

{% block content -%}

Block Content

    {%- block table_contents %}
     Table contents
    <ul>
    {% for li in list_table -%}
    <li>{% block item scoped %}{{ li }}{% endblock %}</li>
    {% endfor %}
    </ul>
    {% endblock table_contents %}

{% endblock content %}


</body>
</html>


