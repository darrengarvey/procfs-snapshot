import logging

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
