
from math import sqrt, log

from django.conf import settings


def comment_rating(upvotes, downvotes):
    total = 1.0 * (upvotes + downvotes)

    if total <= 0:
        return 0.0

    Z = 1.64485  # Zindex Assumes .95 confidence
    phat = 1.0 * upvotes / total
    WilsonScore = (phat + Z * Z / (total * 2) - Z * sqrt((phat * (1.0 - phat) + Z * Z / (total * 4)) / total)) / (1 + Z * Z / total)

    return WilsonScore


def forum_post_rating(upvotes, time_diff):
    # assumptions:
    #       upvotes >= 0
    #       time_diff > 0

    merit = 1.0 * log(1.0 + upvotes, settings.MERIT_JUDGEMENT)
    age = 1.0 * time_diff / settings.AGE_JUDGEMENT

    return merit - age
