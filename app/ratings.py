from math import sqrt


def comment_rating(upvotes, downvotes):
    total = 1.0 * (upvotes + downvotes)

    if total <= 0:
        return 0.0

    Z = 1.64485  # Zindex Assumes .95 confidence
    phat = 1.0 * upvotes / total
    WilsonScore = (phat + Z * Z / (total * 2) - Z * sqrt((phat * (1.0 - phat) + Z * Z / (total * 4)) / total)) / (1 + Z * Z / total)

    return WilsonScore
