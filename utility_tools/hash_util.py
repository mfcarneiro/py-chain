import hashlib as hslib
from json import dumps


class Hash_util:

    @staticmethod
    def hash_block(block):
        """ list comprehension example
        return '-'.join([str(block[key]) for key in block])
        """
        return hslib.sha256(dumps(block, sortkeys=True).encode()).hexdigest()

    @staticmethod
    def hash_string_256(hash_string):
        return hslib.sha256(hash_string).hexdigest()
