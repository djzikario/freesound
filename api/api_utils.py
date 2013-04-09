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

import settings
from piston.utils import rc
import traceback
from models import ApiKey
from piston.emitters import Emitter
from piston.handler import typemapper
import logging

logger = logging.getLogger("api")


class ReturnError(Exception):
    def __init__(self, status_code, type, extra, request):
        self.status_code = status_code
        self.type = type
        self.extra = extra
        self.request = request

def build_error_response(e):

    #logger.error(str(e.status_code) + ' API error: ' + e.type)
    content = {"error": True,
               "type": e.type,
               "status_code": e.status_code,
               "explanation": ""}
    content.update(e.extra)
    response = rc.BAD_REQUEST
    response_format = e.request.GET.get("format", "json")
    em_info = Emitter.get(response_format)
    RequestEmitter = em_info[0]
    emitter = RequestEmitter(content, typemapper, "", "", False)
    response.content = emitter.render(e.request)
    response['Content-Type'] = em_info[1]

    return response


def create_unexpected_error(e, request):
    debug = traceback.format_exc() if settings.DEBUG else str(e)
    logger.error('500 API error: Unexpected')
    return ReturnError(500,
                       "InternalError",
                       {"explanation":
                        "An internal Freesound error ocurred.",
                        "really_really_sorry": True,
                        "debug": debug
                       }, request)


def build_invalid_url(request):
    logger.error('404 API error: Invalid Url')
    return build_error_response(ReturnError(404,
                                            "InvalidUrl",
                                            {"explanation":
                                             "The introduced url is invalid.",},
                                            request))


class MyKeyAuth(object):

    def is_authenticated(self, request):

        try:
            # Try to get the api key
            api_key = request.GET.get('api_key', False)
            if not api_key:

                logger.error('401 API error: Authentication error (no api key supplied)')
                self.error = ReturnError(401, "AuthenticationError",
                                         {"explanation":  "Please include your api key as the api_key GET parameter"},
                                         request)
                return False

            try:
                db_api_key = ApiKey.objects.get(key=api_key, status='OK')

            except ApiKey.DoesNotExist:
                logger.error('401 API error: Authentication error (wrong api key)')
                self.error = ReturnError(401, "AuthenticationError",
                                         {"explanation":  "Supplied api_key does not exist"},
                                         request)
                return False

            request.user = db_api_key.user
            return True

        except Exception, e:
            self.error = create_unexpected_error(e, request)
            return False

    def challenge(self):
        return build_error_response(self.error)


'''
class keyAuth():

    def __init__(self, get_parameter='api_key'): # FROM FREESOUND
        self.get_parameter = get_parameter

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        def decorated_api_func(handler, request, *args, **kargs):
            try:

                # Try to get the api key
                api_key = request.GET.get(self.get_parameter, False)
                if not api_key:
                    logger.error('401 API error: Authentication error (no api key supplied)')
                    raise ReturnError(401, "AuthenticationError",
                                          {"explanation":  "Please include your api key as the api_key GET parameter"},
                                          )
                try:
                    db_api_key = ApiKey.objects.get(key=api_key, status='OK')
                except ApiKey.DoesNotExist:
                    logger.error('401 API error: Authentication error (wrong api key)')
                    raise ReturnError(401, "AuthenticationError",
                                          {"explanation":  "Supplied api_key does not exist"},
                                          )

                request.user = db_api_key.user
                return f(handler, request, *args, **kargs)
            except ReturnError, e:
                return build_error_response(e, request)
            except Exception, e:
                return build_unexpected(e, request)

        return decorated_api_func

'''