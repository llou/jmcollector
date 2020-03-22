def compute_alpha(value, n_volumes, total_volumes):
    """Compute alpha is the algorithm used to sort collection items to be 
    included in the next volume. It works this way:

        * if item value is a 1 it is included only once, as is alpha value
          is 0.1 while not included and 0 afterwards.
        * if item value is a 10 it is included in all volumes as its value
          is 1 for all volumes.
        * for other items we compute the actual state, this is the number
          of times it is included in a volume divided between the number of
          volumes. Then we compute the optival value, this is the proportion
          of volumes that the item should be in, we do it as the value
          divided by ten. Alpha is then computed as the difference of these
          two. 
    
    This is done this way to ensure that items that are in many volumes
    have less alpha than those that are in a few.
    """
    assert(n_volumes <= total_volumes)
    if value == 1:
        if n_volumes:
            return 0
    if value == 10:
        return 1
    if total_volumes == 0:
        return float(value)/10
    state = float(n_volumes)/total_volumes
    optimal = float(value)/10
    return optimal - state


