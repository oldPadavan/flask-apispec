import re

import werkzeug.routing

PATH_RE = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')


def rule_to_path(rule):
    return PATH_RE.sub(r'{\1}', rule.rule)


CONVERTER_MAPPING = {
    werkzeug.routing.UnicodeConverter: ('string', None),
    werkzeug.routing.IntegerConverter: ('integer', 'int32'),
    werkzeug.routing.FloatConverter: ('number', 'float'),
}

DEFAULT_TYPE = ('string', None)


def rule_to_params(rule, overrides=None, *, major_api_version=2):
    overrides = (overrides or {})
    result = [
        argument_to_param(
            argument, rule,
            overrides.get(argument, {}),
            major_api_version=major_api_version)
        for argument in rule.arguments
    ]
    for key in overrides.keys():
        if overrides[key].get('in') in ('header', 'query'):
            overrides[key]['name'] = overrides[key].get('name', key)
            result.append(overrides[key])
    return result


def argument_to_param(argument, rule, override=None, *, major_api_version=2):
    param = {
        'in': 'path',
        'name': argument,
        'required': True,
    }
    type_, format_ = CONVERTER_MAPPING.get(type(rule._converters[argument]), DEFAULT_TYPE)
    schema = {}
    schema['type'] = type_
    if format_ is not None:
        schema['format'] = format_
    if rule.defaults and argument in rule.defaults:
        param['default'] = rule.defaults[argument]
    if major_api_version == 2:
       param.update(schema)
    elif major_api_version == 3:
       param['schema'] = schema
    else:
       raise NotImplementedError("No support for OpenAPI / Swagger Major version {}".format(major_api_version))
    param.update(override or {})
    return param
