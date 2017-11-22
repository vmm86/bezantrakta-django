import errno
import glob
import io
import os
import random
import tempfile
import time
import zlib

from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from django.core.files.move import file_move_safe
try:
    from django.utils.six.moves import cPickle as pickle
except ImportError:
    import pickle


class FileBasedCache(BaseCache):
    cache_suffix = 'djcache'

    def __init__(self, dir, params):
        super(FileBasedCache, self).__init__(params)
        self._dir = os.path.abspath(dir)
        self._createdir()

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        if self.key_exists(key, version):
            return False
        self.set(key, value, timeout, version)
        return True

    def get(self, key, default=None, version=None):
        fname = self._key_to_file(key, version)
        try:
            with io.open(fname, 'rb') as f:
                if not self._is_expired(f):
                    return pickle.loads(zlib.decompress(f.read()))
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise
        return default

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        app_name = self.app_name_from_key(key)
        # print('set app_name: `', app_name, '`\n', sep='')
        self._createdir(app_name)  # Cache dir can be deleted at any time.
        fname = self._key_to_file(key, version)
        self._cull()  # make some room if necessary
        fd, tmp_path = tempfile.mkstemp(dir=self._dir)
        renamed = False
        try:
            with io.open(fd, 'wb') as f:
                expiry = self.get_backend_timeout(timeout)
                f.write(pickle.dumps(expiry, pickle.HIGHEST_PROTOCOL))
                f.write(zlib.compress(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)))
            file_move_safe(tmp_path, fname, allow_overwrite=True)
            renamed = True
        finally:
            if not renamed:
                os.remove(tmp_path)

    def delete(self, key, version=None):
        # print('delete key: ', key)
        # print('delete version: ', version)
        self._delete(self._key_to_file(key, version))

    def _delete(self, fname):
        if not fname.startswith(self._dir) or not os.path.exists(fname):
            return
        try:
            os.remove(fname)
        except OSError as e:
            # ENOENT can happen if the cache file is removed (by another
            # process) after the os.path.exists check.
            if e.errno != errno.ENOENT:
                raise

    def key_exists(self, key, version=None):
        fname = self._key_to_file(key, version)
        if os.path.exists(fname):
            with io.open(fname, 'rb') as f:
                return not self._is_expired(f)
        return False

    def _cull(self):
        """
        Removes random cache entries if max_entries is reached at a ratio
        of num_entries / cull_frequency. A value of 0 for CULL_FREQUENCY means
        that the entire cache will be purged.
        """
        filelist = self._list_cache_files()
        num_entries = len(filelist)
        if num_entries < self._max_entries:
            return  # return early if no culling is required
        if self._cull_frequency == 0:
            return self.clear()  # Clear the cache when CULL_FREQUENCY = 0
        # Delete a random selection of entries
        filelist = random.sample(filelist, int(num_entries / self._cull_frequency))
        for fname in filelist:
            self._delete(fname)

    def _createdir(self, app_name=None):
        if app_name is None:
            cache_path = self._dir
        else:
            cache_path = os.path.join(self._dir, app_name)

        if not os.path.exists(cache_path):
            try:
                os.makedirs(cache_path, 0o700)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise EnvironmentError(
                        "Cache directory '{}' does not exist and could not be created".format(cache_path)
                    )

    def _key_to_file(self, key, version=None):
        """
        Convert a key into a cache file path.

        key = {prefix}:{version}:{key}
        :1:django_compressor.templatetag.d5c553c2927f.inline.js
        """
        key = self.make_key(key, version=version)
        app_name = self.app_name_from_key(key)
        # print('_key_to_file app_name: `', app_name, '`\n', sep='')
        self.validate_key(key)
        return os.path.join(
            self._dir,
            app_name,
            '{key}.{cache_suffix}'.format(key=key, cache_suffix=self.cache_suffix)
        )

    def clear(self):
        """
        Remove all the cache files.
        """
        if not os.path.exists(self._dir):
            return
        for fname in self._list_cache_files():
            self._delete(fname)

    def _is_expired(self, f):
        """
        Takes an open cache file and determines if it has expired,
        deletes the file if it is has passed its expiry time.
        """
        exp = pickle.load(f)
        if exp is not None and exp < time.time():
            f.close()  # On Windows a file has to be closed before deleting
            self._delete(f.name)
            return True
        return False

    def _list_cache_files(self):
        """
        Get a list of paths to all the cache files. These are all the files
        in the root cache dir that end on the cache_suffix.
        """
        if not os.path.exists(self._dir):
            return []
        filelist = [
            os.path.join(self._dir, fname) for fname in glob.glob1(self._dir, '*.{}'.format(self.cache_suffix))
        ]
        return filelist

    # def make_key(self, key, version=None):
    #     """Constructs the key used by all other methods.
    #     By default it uses the `key_func` to generate a key
    #     (which, by default, prepends the `key_prefix' and 'version').
    #     A different key function can be provided at the time of cache construction;
    #     alternatively, you can subclass the cache backend to provide custom key making behavior.
    #     """
    #     version = self.version if version is None else version
    #     return '{}:{}:{}'.format(self.key_prefix, version, key)
    #     # return str(key)

    def app_name_from_key(self, key):
        """
        Get app name from the key name.
        """
        app_name = key.split(':')[2] if ':' in key else key
        app_name = app_name.split('.')[0]
        return app_name
