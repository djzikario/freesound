from django import template
from django.conf import settings
import re

register = template.Library()

mapping = """8-) 8) cool
:'( cry
:D :-D grin
=) happy
:-| :| neutral
:( :-( sad
:) :-) smile
:P :-P tongue
:S :-S weird
;) ;-) wink
:O :-O woot"""

d = []
for emoticons, name in map(lambda x: (x[:-1], x[-1]), [x.split() for x in mapping.lower().split("\n")]):
    for emoticon in emoticons:
        d.append((emoticon,name))

emoticons = dict(d)

def smiley_replace(matchobj):
    try:
        expression = emoticons[matchobj.group(0).lower()]
        return "<img src=\"%simages/smileys/%s.png\" alt=\"%s\" class=\"smiley\" />" % (settings.MEDIA_URL, expression, expression)
    except KeyError:
        return matchobj.group(0)

smiley_replacer = re.compile("=\)|;\-?\)|8\-?\)|:'\(|:\-?[OoPpSsDd\)\(\|]")

@register.filter
def smileys(string):
    return smiley_replacer.sub(smiley_replace, string)
smileys.is_safe = True