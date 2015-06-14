import ast
import json
import math

def factors_of(numbers):
    '''
    Get the factors of a list of numbers as a dictionary. The keys
    are the numbers, and the values are the factors of the key that
    are in the numbers list.
    '''
    return dict(
        (num, [i for i in numbers if i != num and num % i == 0])
        for num in numbers
    )

def factors_for(numbers):
    '''
    Get the factors for a list of numbers as a dictionary. The keys
    are the numbers, and the values are the factors for the key that
    are in the numbers list.
    '''
    return dict(
        (num, [i for i in numbers if i != num and i % num == 0])
        for num in numbers
    )

class Factorize(object):
    def __init__(self, use_file_cache=True, use_cache=True, verbose=True):
        # if we are using a file cache, we're implicitly using our memory cache
        self.use_cache = use_cache or use_file_cache
        self.use_file_cache = use_file_cache
        self.verbose = verbose
        self._initialize_cache('of_cache')
        self._initialize_cache('for_cache')

    def _cache_key(self, numbers):
        '''
        Return the cache key for a list of numbers by
        converting it to a frozenset.
        We use a frozen set because it can:
        1. be used as a dictionary key for our cache, and
        2a. ignores issues of duplicate numbers or sorting.
        2b. sorting is the enemy.
        '''
        assert isinstance(numbers, list), "You must provide a list!"
        return frozenset(numbers)


    def _jsonized_cache(self, cache_name):
        '''
        JSON cannot support non-string keys for dictionaries. When we
        import the cache, we cannot use 'frozenset' because we are using
        literal_eval which does not support constructors. As such, we store
        the keys as tuples instead of frozensets, knowing we will restore their
        status when we initialize the cache.
        '''
        return dict(
            (str(tuple(k)), v)
            for k, v in getattr(self, cache_name).iteritems()
        )


    def _initialize_cache(self, cache_name):
        '''
        Load from a cache file into a named cache.
        Note that we store our global cache in this single file, and that
        we only read it once (on initialization) and write to it once.
        This is because having each list's values stored in its own individual
        file necessitates constant reading from and writing to disk; although at
        some point the cache will theoretically grow tremendous enough to
        cause slow-downs, those will only be at spin-up and spin-down time
        and at no point should the program touch disk
        
        A better solution, of course, would be to just use memcached. It also
        may be better to just store the list of all factors for every number
        in one monolithic file and then to filter the results based on the
        passed-in lists, but that could get very slow when dealing with large
        sets of large numbers. More tests would need to be done.
        
        The requirements of the programming challenge explicitly stated storing
        the lists of numbers as keys and so that is what we do here.
        '''
        # this will create the file if it does not exist.
        if not self.use_file_cache:
            setattr(self, cache_name, {})
            return
            
        try:
            with open('./%s.json' % cache_name, 'w+') as fh:
                # see self._jsonized_cache.__doc__ for explanation
                # of why we are using ast.literal_eval and frozenset
                setattr(self, cache_name, dict(
                    frozenset(ast.literal_eval(k))
                    for k, v in json.load(fh).iteritems()
                ))
                if self.verbose:
                    print "Loaded %s from %s.json, got %i lists..." % (
                        cache_name, cache_name, len(getattr(self, cache_name).keys())
                    )
        except: # no or bad current file content.
            setattr(self, cache_name, {})


    def _save_cache(self, cache_name):
        ''' Save one of our caches out to a file. '''
        if self.verbose:
            print "Saving %i lists from %s to %s.json..." % (
                len(getattr(self, cache_name).keys()), cache_name, cache_name
            )
        data = self._jsonized_cache(cache_name)
        with open('./%s.json' % cache_name, 'w+') as fh:
            json.dump(data, fh)


    def get_factors_for(self, numbers):
        '''
        Get the factors for a list of numbers, storing into the
        for_cache cache key if it's not already there.
        '''
        if not self.use_cache:
            return factors_for(numbers)

        key = self._cache_key(numbers)

        if key not in self.for_cache:
            if self.verbose:
                print "List not found, adding to for cache..."
            self.for_cache[key] = factors_for(numbers)

        return self.for_cache[key]


    def get_factors_of(self, numbers):
        '''
        Get the factors of a list of numbers, storing into the
        of_cache cache key if it's not already there.
        '''
        if not self.use_cache:
            return factors_of(numbers)

        key = self._cache_key(numbers)

        if key not in self.of_cache:
            if self.verbose:
                print "List not found, adding to of cache..."
            self.of_cache[key] = factors_of(numbers)

        return self.of_cache[key]        


    def __del__(self):
        if self.use_file_cache:
            self._save_cache('of_cache')
            self._save_cache('for_cache')
