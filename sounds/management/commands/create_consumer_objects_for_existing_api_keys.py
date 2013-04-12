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

from django.core.management.base import BaseCommand
from api.models import ApiKey
from piston.models import Consumer

class Command(BaseCommand):
    args = ''
    help = 'Create a consumer object for each existing api_key which does not have an assigned consumer'

    def handle(self, *args, **options):
        for key in ApiKey.objects.all():
            try:
                print "- Key with id %i has already a consumer with (id=%i)" % (key.id, key.consumer.id)
            except:
                print "- Creating consumer for key with id %i..." % key.id,
                c = Consumer(name=key.name,
                             description=key.description,
                             status="accepted",
                             user=key.user,
                             api_key=key)
                c.generate_random_codes()
                c.save()

                print "done! (id=%i)" % c.id




