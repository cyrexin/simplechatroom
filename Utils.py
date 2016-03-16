import re


class Utils:
    @staticmethod
    def is_number(var):
        args = re.match( r'^\d+$', var, re.M|re.I)
        if args:
            return True
        else:
            return False
