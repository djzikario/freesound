# -*- coding: utf-8 -*-

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

from django.contrib import admin
from api.models import ApiKey
from piston.models import Nonce, Consumer, Token


class ApiKeyAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',) 
    search_fields = ('=user__username', )
    list_filter = ('status', )
    list_display = ("key", "user", "status")

admin.site.register(ApiKey, ApiKeyAdmin)

admin.site.register(Consumer)
admin.site.register(Nonce)
admin.site.register(Token)