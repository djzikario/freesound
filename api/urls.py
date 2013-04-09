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

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from handlers import *
from views import create_api_key
from api_utils import build_invalid_url, MyKeyAuth, build_error_response

### TODO
# make Api respond when raise "ReturnError" is thrown and in general any Exception (unexpeced error)
# Not sure where this should be, but it sould be common in both authentication methods


# Key-based authentication resources
myKeyAuth = MyKeyAuth()
class KeyAuthentication(Resource):
    def __init__(self, *args, **kwargs):
        super(KeyAuthentication, self).__init__(authentication=myKeyAuth, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        response = super(KeyAuthentication, self).__call__(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        return response

# Three legged authentication
threeLeggedAuth = OAuthAuthentication(realm='api')
class ThreeLeggedAuth(Resource):
    def __init__(self, *args, **kwargs):
        super(ThreeLeggedAuth, self).__init__(authentication=threeLeggedAuth, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        response = super(ThreeLeggedAuth, self).__call__(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        return response


urlpatterns = patterns('',
    # sounds
    url(r'^sounds/search/$',                                        KeyAuthentication(SoundSearchHandler),         name='api-search'),
    url(r'^sounds/content_search/$',                                KeyAuthentication(SoundContentSearchHandler),  name='api-content-search'),
    url(r'^sounds/(?P<sound_id>\d+)/$',                             KeyAuthentication(SoundHandler),               name='api-single-sound'),
    url(r'^sounds_2/(?P<sound_id>\d+)/$',                           ThreeLeggedAuth(SoundHandlerTEST),             name='api-single-sound-three-legged'),
    url(r'^sounds/(?P<sound_id>\d+)/analysis/$',                    KeyAuthentication(SoundAnalysisHandler),       name='api-sound-analysis'),
    url(r'^sounds/(?P<sound_id>\d+)/analysis(?P<filter>/[\w\/]+)/$',KeyAuthentication(SoundAnalysisHandler),       name='api-sound-analysis-filtered'),
    # For future use (when we serve analysis files through autenthication)
    #url(r'^sounds/(?P<sound_id>\d+)/analysis_frames/$',            KeyAuthentication(SoundAnalysisFramesHandler), name='api-sound-analysis-frames'),
    #url(r'^sounds/(?P<sound_id>\d+)/serve/$',                       ThreeLeggedAuth(SoundServeHandler),           name='api-sound-serve'),
    url(r'^sounds/(?P<sound_id>\d+)/similar/$',                     KeyAuthentication(SoundSimilarityHandler),     name='api-sound-similarity'),
    url(r'^sounds/geotag/$',                                        KeyAuthentication(SoundGeotagHandler),         name='api-sound-geotag'),
    
    # users
    url(r'^people/(?P<username>[^//]+)/$',                                                     KeyAuthentication(UserHandler),                    name='api-single-user'),
    url(r'^people/(?P<username>[^//]+)/sounds/$',                                              KeyAuthentication(UserSoundsHandler),              name='api-user-sounds'),
    url(r'^people/(?P<username>[^//]+)/packs/$',                                               KeyAuthentication(UserPacksHandler),               name='api-user-packs'),
    url(r'^people/(?P<username>[^//]+)/bookmark_categories/$',                                 KeyAuthentication(UserBookmarkCategoriesHandler),  name='api-user-bookmark-categories'),
    url(r'^people/(?P<username>[^//]+)/bookmark_categories/(?P<category_id>\d+)/sounds/$',     KeyAuthentication(UserBookmarkCategoryHandler),    name='api-user-bookmark-category'),
    url(r'^people/(?P<username>[^//]+)/bookmark_categories/uncategorized/sounds/$',            KeyAuthentication(UserBookmarkCategoryHandler),    name='api-user-bookmark-uncategorized'),

    # packs
    url(r'^packs/(?P<pack_id>\d+)/$',                               KeyAuthentication(PackHandler),           name='api-single-pack'),
    url(r'^packs/(?P<pack_id>\d+)/serve/$',                         KeyAuthentication(PackServeHandler),      name='api-pack-serve'),
    url(r'^packs/(?P<pack_id>\d+)/sounds/$',                        KeyAuthentication(PackSoundsHandler),     name='api-pack-sounds'),

    # cc-mixter pool
    url(r'^pool/search$',                                           SoundPoolSearchHandler(),   name='api-pool-search'),
    url(r'^pool/search/$',                                          SoundPoolSearchHandler(),   name='api-pool-search-slash'),
    url(r'^pool/info$',                                             SoundPoolInfoHandler(),     name='api-pool-info'),
    url(r'^pool/info/$',                                            SoundPoolInfoHandler(),     name='api-pool-info-slash'),
    
    # website
    url(r'^apply/$', create_api_key),
)
# piston, oauth urls
urlpatterns += patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$', 'oauth_request_token'),
    url(r'^oauth/authorize/$', 'oauth_user_auth'),
    url(r'^oauth/access_token/$', 'oauth_access_token'),
)

# anything else (invalid urls)
urlpatterns += patterns(
    '',
    url(r'/$', build_invalid_url ),
)

