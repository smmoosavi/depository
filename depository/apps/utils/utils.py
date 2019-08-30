from _sha1 import sha1


def sub_dict(data, keys):
    new_dict = {}
    for key in keys:
        if key in data:
            new_dict[key] = data[key]
    return new_dict


class Encryption(object):
    def cesar(self, text, step=20, reverse=False):
        result = ''
        if reverse:
            step = (-1) * step
        for i in text:
            new_c = chr(ord(i) + step)
            result += new_c
        return result[::-1]
