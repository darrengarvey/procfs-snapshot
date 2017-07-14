import logging
import re

logging.basicConfig(format='%(asctime)-15s %(levelname)s %(filename)s:%(lineno)d %(message)s')
LOGGER = logging.getLogger('stats-snapshot')


def find_all_subclasses(classType):
    subclasses = dict()
    stack = [classType]
    while stack:
        parent = stack.pop()
        for child in parent.__subclasses__():
            name = child.__name__
            if not subclasses.has_key(name):
                subclasses[name] = child
                stack.append(child)
    return subclasses


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def camel_case_to_underscore(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    s2 = all_cap_re.sub(r'\1_\2', s1).lower()
    return re.sub(r'(_)\1+', r'\1', s2)
