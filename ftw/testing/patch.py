import gc
import six


def patch_refs(scope, original_name, replacement):
    """Patch a method or function and all references to it."""
    original = getattr(scope, original_name)
    setattr(scope, original_name, replacement)
    # replace any other references
    global_replace(original, replacement)


def global_replace(original, replacement):
    """Replace all references to object 'original' with object
    'replacement' in all dictionaries (i.e. module and class scopes for
    functions / methods).

    Based on Labix mocker's global_replace().
    """
    for referrer in gc.get_referrers(original):
        if type(referrer) is not dict:
            continue

        if referrer.get("__patch_refs__", True):
            for key, value in list(six.iteritems(referrer)):
                if value is original:
                    referrer[key] = replacement
