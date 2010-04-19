##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re
from zope.i18nmessageid import Message

class TranslationString(Message):
    """ The constructor for a :term:`translation string`.  A
    translation string is a Unicode-like object that has some extra
    metadata.

    This constructor accepts one required argument named ``text``.
    ``text`` must be the default text of the translation string,
    optionally including replacement markers such as ``${foo}``.

    Optional keyword arguments to this object's constructor include
    ``msgid``, ``mapping`` and ``domain``.

    ``mapping``, if supplied, must be a dictionarylike object which
    represents the replacement values for any replacement markers
    found within the ``text`` value of this

    ``msgid`` represents an explicit :term:`message identifier` for
    this translation string.  Usually, the ``text`` of a translation
    string serves as its message identifier.  However, using this
    option you can pass an explicit message identifier, usually a
    simple string.  This is useful when the ``text`` of a translation
    string is too complicated or too long to be used as a translation
    key. If ``msgid`` is ``None`` (the default), the ``msgid`` value
    used by this translation string will be assumed to be the value of
    ``text``.

    ``domain`` represents the :term:`translation domain`.  By default,
    the translation domain is ``None``, indicating that this
    translation string is associated with no translation domain.

    After a translation string is constructed, its ``text`` value is
    available as the ``default`` attribute of the object, the
    ``msgid`` is available as the ``msgid`` attribute of the object,
    the ``domain`` is available as the ``domain`` attribute, and the
    ``mapping`` is available as the ``mapping`` attribute.  The object
    otherwise behaves much like a Unicode string.
    """
    def __new__(cls, text, mapping=None, msgid=None, domain=None):
        if msgid is None:
            msgid = text
        return Message.__new__(cls, msgid, domain=domain, default=text,
                               mapping=mapping)

class TranslationStringFactory(object):
    """ Create a factory which will generate translation strings
    without requiring that each call to the factory be passed a
    ``domain`` value.  A single argument is passed to this class'
    constructor: ``domain``.  This value will be used as the
    ``domain`` values of :class:`internatl.TranslationString` objects
    generated by the ``__call__`` of this class.  The ``text``,
    ``mapping``, and ``msgid`` values provided to the ``__call__``
    method of an instance of this class have the meaning as described
    by the constructor of the :class:`internatl.TranslationString`"""
    def __init__(self, domain):
        self.domain = domain

    def __call__(self, text, mapping=None, msgid=None):
        """ Provided a text (Unicode or :term:`translation string`)
        object, and optionally a mapping object, and a :term:`message
        identifier`, return a :term:`translation string` object. """
        return TranslationString(text, mapping=mapping, msgid=msgid,
                                 domain=self.domain)
                               
class ChameleonTranslate(object):
    """ Register an instance of this class as a Chameleon template
    'translate' function (e.g. the ``translate`` argument to the
    ``chameleon.zpt.template.PageTemplate`` constructor) allow our
    translator to drive template translation.  A single required
    argument ``translator`` is passsed to this class' constructor.  It
    should be capable of accepting a :term:`translation string` and
    returning a completely interpolated and translated Unicode string."""
    def __init__(self, translator):
        self.translator = translator
        
    def __call__(self, text, domain=None, mapping=None, context=None,
                 target_language=None, default=None):
        if text is None:
            return None
        if default is None:
            default = text
        if mapping is None:
            mapping = {}
        if not hasattr(text, 'mapping'):
            text = TranslationString(default, mapping=mapping, msgid=text, 
                                     domain=domain)
        return self.translator(text)

NAME_RE = r"[a-zA-Z][-a-zA-Z0-9_]*"

_interp_regex = re.compile(r'(?<!\$)(\$(?:(%(n)s)|{(%(n)s)}))'
    % ({'n': NAME_RE}))
    
def interpolate(text, mapping=None):
    """ Interpolate a string with one or more *replacement markers*
    (``${foo}`` or ``${bar}``).  Note that if a :term:`translation
    string` is passed to this function, it will be implicitly
    converted back to the Unicode object."""
    def replace(match):
        whole, param1, param2 = match.groups()
        return unicode(mapping.get(param1 or param2, whole))

    if not text or not mapping:
        return text

    return _interp_regex.sub(replace, text)
