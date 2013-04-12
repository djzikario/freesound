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

### Error handling
##################


class ReturnError(Exception):
    def __init__(self, status_code, type, extra):
        self.status_code = status_code
        self.type = type
        self.extra = extra


def build_error_response(e, request=None):

    content = {"error": True,
               "type": e.type,
               "status_code": e.status_code,
               "explanation": ""}
    content.update(e.extra)

    logger.error("%i %s: %s" % (content['status_code'], content['type'], content['explanation']))

    response = rc.BAD_REQUEST
    if request:
        response_format = request.GET.get("format", "json")
    else:
        response_format = "json"
    em_info = Emitter.get(response_format)
    RequestEmitter = em_info[0]
    emitter = RequestEmitter(content, typemapper, "", "", False)
    response.content = emitter.render(request)
    response['Content-Type'] = em_info[1]

    return response


def create_unexpected_error(e):
    if settings.DEBUG:
        debug = traceback.format_exc() if settings.DEBUG else str(e)
    else:
        debug = "-"
    #logger.error('500 API error: Unexpected')
    return ReturnError(500,
                       "InternalError",
                       {"explanation": "An internal Freesound error ocurred.",
                        "really_really_sorry": True,
                        "debug": debug})


def build_invalid_url(request):
    logger.error('404 API error: Invalid Url')
    return build_error_response(ReturnError(404,
                                            "InvalidUrl",
                                            {"explanation": "The introduced url is invalid.",}), request)


class catchExceptionsAndReturnAsErrors():

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        def decorated_api_func(handler, request, *args, **kargs):
            try:
                #request.user = db_api_key.user
                result = f(handler, request, *args, **kargs)
                return result
            except ReturnError, e:
                return build_error_response(e, request)
            except Exception, e:
                return build_error_response(create_unexpected_error(e), request)

        return decorated_api_func


### Standard key authentication
###############################

class MyKeyAuth(object):

    def is_authenticated(self, request):

        try:
            # Try to get the api key
            api_key = request.GET.get('api_key', False)
            if not api_key:

                #logger.error('401 API error: Authentication error (no api key supplied)')
                self.error = ReturnError(401, "AuthenticationError",
                                         {"explanation": "Please include your api key as the api_key GET parameter"})
                return False

            try:
                db_api_key = ApiKey.objects.get(key=api_key, status='OK')

            except ApiKey.DoesNotExist:
                #logger.error('401 API error: Authentication error (wrong api key)')
                self.error = ReturnError(401, "AuthenticationError",
                                         {"explanation": "Supplied api_key does not exist"})
                return False

            request.developer_user = db_api_key.user
            request.username = request.developer_user
            return True

        except Exception, e:
            self.error = create_unexpected_error(e)
            return False

    def challenge(self, request):
        return build_error_response(self.error, request)

