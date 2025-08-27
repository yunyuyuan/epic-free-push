{% for game in games %}
*游戏*：[{{ game.title }}]({{ game.link }})
*描述*：{{ game.description }}
*起止时间*：{{ game.start }} ~ {{ game.end }}
*状态*：{% if game.upcoming %}未开始{% else %}*进行中*{% endif %}
==============
{% endfor %}