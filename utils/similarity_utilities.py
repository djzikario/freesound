import settings, traceback, logging
from sounds.models import Sound
from django.core.cache import cache
from similarity.client import Similarity

logger = logging.getLogger('web')

def get_similar_sounds(sound, preset, num_results = settings.SOUNDS_PER_PAGE ):

    if preset not in ['lowlevel', 'music']:
        preset = settings.DEFAULT_SIMILARITY_PRESET

    cache_key = "similar-for-sound-%s-%s" % (sound.id, preset)

    # Don't use the cache when we're debugging
    if settings.DEBUG:
        similar_sounds = False
    else:
        similar_sounds = cache.get(cache_key)

    if not similar_sounds:
        try:
            similar_sounds = [ [int(x[0]),float(x[1])] for x in Similarity.search(sound.id, preset, settings.SIMILAR_SOUNDS_TO_CACHE)]
        except Exception, e:
            logger.debug('Could not get a response from the similarity service (%s)\n\t%s' % \
                         (e, traceback.format_exc()))
            similar_sounds = []

        if len(similar_sounds) > 0:
            cache.set(cache_key, similar_sounds, settings.SIMILARITY_CACHE_TIME)

    return similar_sounds[0:num_results]
