from __future__ import absolute_import, unicode_literals
import sys
import base64
import json

try:
    import cPickle as pickle
except ImportError:
    import pickle

from difflib import SequenceMatcher
from django.db import models
from django.utils.encoding import force_unicode

#from django.utils.encoding import smart_unicode
# Google Diff Match Patch library
# http://code.google.com/p/google-diff-match-patch
if sys.version_info > (3, ):
    from .vendor.diff_match_patch.python3.diff_match_patch import diff_match_patch
else:
    from .vendor.diff_match_patch.python2.diff_match_patch import diff_match_patch

from versioning import _registry

try:
    str = unicode  # Python 2.* compatible
    string_types = (basestring,)
    integer_types = (int, long)
except NameError:
    string_types = (str,)
    integer_types = (int,)

PICKLED_MARKER = 'pickled:'
STR_MARKER = 'str:'

dmp = diff_match_patch()


def encode(val):
    if not isinstance(val, string_types):
        # XML? JSON? pickle?
        return PICKLED_MARKER + base64.standard_b64encode(
            pickle.dumps(val, protocol=pickle.HIGHEST_PROTOCOL)
        ).decode('ascii')
    return STR_MARKER + force_unicode(val)  # prevent to user to falsify PICKLED_MARKER


def decode(val):
    if val.startswith(PICKLED_MARKER):
        try:
            return pickle.loads(base64.standard_b64decode(val[len(PICKLED_MARKER):].encode('ascii')))
        except Exception:
            pass
    elif val.startswith(STR_MARKER):
        return val[len(STR_MARKER):]
    return val


def revisions_for_object(instance):
    from .models import Revision
    return Revision.objects.get_for_object(instance)


def diff(txt_prev, txt_next):
    """Create a 'diff' from txt_prev to txt_new."""
    patch = dmp.patch_make(txt_next, txt_prev)
    return dmp.patch_toText(patch)


def set_field_data(obj, field, data):
    field_inst = obj._meta.get_field(field)
    # data = decode(data)
    if field_inst.null and data == 'None':
        data = None
    elif isinstance(field_inst, models.ManyToManyField):
        data = json.loads(data)
    elif isinstance(field_inst, (models.DateTimeField, models.DateField, models.TimeField)) and not data and field_inst.null:
        data = None
    else:
        data = field_inst.to_python(data)
    setattr(obj, field_inst.attname, data)


def get_field_data(obj, field):
    """Returns field's data"""
    # return encode(obj._meta.get_field(field)._get_val_from_obj(obj))
    field_inst = obj._meta.get_field(field)
    if isinstance(field_inst, models.ManyToManyField) and not obj.pk:
        return '[]'
    return field_inst.value_to_string(obj)


def get_field_str(obj, field):
    """Returns field's string"""
    return obj._meta.get_field(field).value_to_string(obj)


def obj_diff(obj_prev, obj_next):
    """Create a 'diff' from obj_prev to obj_new."""
    model = obj_next.__class__
    fields = _registry[model]
    lines = []
    for field in fields:
        data_prev = get_field_data(obj_prev, field)
        data_next = get_field_data(obj_next, field)
        # data_diff = unified_diff(data_prev.splitlines(), data_next.splitlines(), context=3)
        data_diff = diff(data_prev, data_next)
        lines.extend(["--- {0}.{1}".format(model.__name__, field),
                     "+++ {0}.{1}".format(model.__name__, field)])
        lines.append(data_diff.strip())

    return "\n".join(lines)


def apply_diff(obj, delta):
    model = obj.__class__
    fields = _registry[model]
    diffs = diff_split_by_fields(delta)
    for key, diff in diffs.items():
        model_name, field_name = key.split('.')
        if model_name != model.__name__ or field_name not in fields:
            continue
        content = get_field_data(obj, field_name)
        patch = dmp.patch_fromText(diff)
        content = dmp.patch_apply(patch, content)[0]
        set_field_data(obj, field_name, content)


def obj_is_changed(obj_prev, obj_next):
    """Returns True, if watched attributes of obj1 deffer from obj2."""
    model = obj_next.__class__
    fields = _registry[model]
    for field in fields:
        original_data = get_field_data(obj_next, field)
        new_data = get_field_data(obj_prev, field)
        if original_data != new_data:
            return True
    return False


def display_diff(obj_prev, obj_next):
    """Returns a HTML representation of the diff."""
    model = obj_next.__class__
    fields = _registry[model]

    result = []
    for field_name in fields:
        result.append("<b>{0}</b>".format(field_name))
        diffs = dmp.diff_main(
            get_field_str(obj_prev, field_name),
            get_field_str(obj_next, field_name)
        )
        dmp.diff_cleanupSemantic(diffs)
        result.append(dmp.diff_prettyHtml(diffs))
    return "<br />\n".join(result)


def diff_split_by_fields(txt):
    """Returns dictionary object, key is fieldname, value is it's diff"""
    result = {}
    current = None
    lines = txt.split("\n")
    for line in lines:
        if line[:4] == "--- ":
            continue
        if line[:4] == "+++ ":
            line = line[4:].strip()
            result[line] = current = []
            continue
        if current is not None:
            current.append(line)
    for k, v in result.items():
        result[k] = "\n".join(v)
    return result


def unified_diff(fromlines, tolines, context=None):
    """
    Generator for unified diffs. Slightly modified version from Trac 0.11.
    """
    matcher = SequenceMatcher(None, fromlines, tolines)
    for group in matcher.get_grouped_opcodes(context):
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        if i1 == 0 and i2 == 0:
            i1, i2 = -1, -1  # add support
        yield '@@ -{0:d},{1:d} +{2:d},{3:d} @@'.format(i1 + 1, i2 - i1, j1 + 1, j2 - j1)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in fromlines[i1:i2]:
                    yield ' ' + line
            else:
                if tag in ('replace', 'delete'):
                    for line in fromlines[i1:i2]:
                        yield '-' + line
                if tag in ('replace', 'insert'):
                    for line in tolines[j1:j2]:
                        yield '+' + line
