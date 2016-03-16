import hashlib


class Encrypt:

    @staticmethod
    def create_signature(data):
        shared_private_key = "4119ProgrammingAssignment1"
        return hashlib.sha1(data + "," + shared_private_key).hexdigest()
