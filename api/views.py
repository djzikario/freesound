#
# Freesound is (c) MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
#
# Freesound is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Freesound is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     See AUTHORS file.
#

from forms import ApiKeyForm
from models import ApiKey
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from piston.models import Token
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import datetime

@login_required
def create_api_key(request):
    if request.method == 'POST':
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            db_api_key = ApiKey()
            db_api_key.user = request.user
            db_api_key.description = form.cleaned_data['description']
            db_api_key.name        = form.cleaned_data['name']
            db_api_key.url         = form.cleaned_data['url']
            db_api_key.accepted_tos= form.cleaned_data['accepted_tos']
            db_api_key.save()
            form = ApiKeyForm()
    else:
        form = ApiKeyForm()
    return render_to_response('api/apply_key.html', 
                              { 'user': request.user, 'form': form }, 
                              context_instance=RequestContext(request))


def request_token_ready(request, token):
    error = request.GET.get('error', '')

    ctx = RequestContext(request, {
        'error': error,
        'token': token
    })
    return render_to_response(
        'piston/request_token_ready.html',
        context_instance = ctx
    )


@login_required
def access_tokens(request):
    user = request.user
    tokens_raw = Token.objects.filter(user=user, token_type=2).order_by('-timestamp')
    tokens = []
    token_names = []
    for token in tokens_raw:
        if not token.consumer.name in token_names:
            tokens.append({
                'consumer_name': token.consumer.name,
                'date': datetime.datetime.fromtimestamp(int(token.timestamp)).strftime('%d-%m-%Y'),
                'consumer_key': token.consumer.key,
                'enabled': token.enabled,
            })
        token_names.append(token.consumer.name)

    return render_to_response('api/access_tokens.html',
                              {'user': request.user, 'tokens': tokens},
                              context_instance=RequestContext(request))


@login_required
def revoke_permission(request, consumer_key):
    user = request.user
    tokens = Token.objects.filter(user=user, consumer__key=consumer_key, token_type=2)
    for token in tokens:
        token.enabled = False
        token.save()

    return HttpResponseRedirect(reverse("access-tokens"))

@login_required
def give_permission(request, consumer_key):
    user = request.user
    tokens = Token.objects.filter(user=user, consumer__key=consumer_key, token_type=2)
    for token in tokens:
        token.enabled = True
        token.save()

    return HttpResponseRedirect(reverse("access-tokens"))