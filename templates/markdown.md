| 游戏 | 起止时间 | 状态 |
|:---:|:---:|:---:|{% for game in games %}
| ![cover]({{ game.cover }})[{{ game.title }}]({{ game.link }}) | **{{ game.start }}** ~ **{{ game.end }}** | {% if game.upcoming %}未开始{% else %}进行中{% endif %} |{% endfor %}
