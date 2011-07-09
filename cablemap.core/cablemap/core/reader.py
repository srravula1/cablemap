# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 -- Lars Heuer <heuer[at]semagia.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the project name nor the names of the contributors may be 
#       used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""\
This module extracts information from cables.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - <http://www.semagia.com/>
:license:      BSD license
"""
import os
import codecs
import re
import logging
from cablemap.core.constants import REFERENCE_ID_PATTERN, MALFORMED_CABLE_IDS

logger = logging.getLogger('cablemap.core.reader')

# Indicates the max. index where the reader tries to detect the subject/TAGS/references
_MAX_HEADER_IDX = 1200

#
# Cables w/o tags
#
_CABLES_WITHOUT_TAGS = (
    '06KABUL3934', '08BEIJING3662', '09ROME878', '09ROME1048', '08ROME451',
    '08ROME525', '04QUITO2502', '04QUITO2879', '05PANAMA1589', '06KABUL5653',
    '07PANAMA400', '07PANAMA946', '01CAIRO5770',
    )

_CABLES_WITHOUT_TO = (
    '08MONTERREY468', '09TIJUANA1116', '08STATE125686', '06WELLINGTON633',
    '06WELLINGTON652', '08STATE34306',
    )

_CABLES_WITH_MALFORMED_SUMMARY = (
    '09CAIRO2133', '06BUENOSAIRES2711', '08BUENOSAIRES1305', '07ATHENS2386',
    '09SOFIA716',
    )

_CABLE_ID_SUBJECT_PATTERN = re.compile('^([0-9]+[^:]+):\s(.+)$')

_CABLE_SUBJECT_FIXES = dict([_CABLE_ID_SUBJECT_PATTERN.match(l).groups() for l in codecs.open(os.path.join(os.path.dirname(__file__), 'subjects.txt'), 'rb', 'utf-8') if l and not l.startswith(u'#')])

_CABLE_FIXES = {
    '08MANAMA492': # (08ECTION01OF02MANAMA492)
        (r'TORUEHC/SECSTATE', u'TO RUEHC/SECSTATE'),
    '08ECTION01OF02MANAMA492':
        (r'TORUEHC/SECSTATE', u'TO RUEHC/SECSTATE'),
    '08TRIPOLI402':
        (ur'JAMAHIRIYA-STYLE\s+Q: A\) TRIPOLI', u'JAMAHIRIYA-STYLE \nREF: A) TRIPOLI'),
    '07HAVANA252':
        (ur'XXXNEED A MILLION', u'XXX NEED A MILLION'),
    '09BEIJING1176':
        (ur'XXXDISCUSSES', u'XXX DISCUSSES'),
    '09BEIJING2438':
        (ur'NEGOTIATE SE\s+CRETLY', u'NEGOTIATE SECRETLY'),
    '09STATE30049':
        (ur'Secretary Clinton’s March 24, 2009 \n\n', u'Secretary Clinton’s March 24, 2009 \n'),
    '09CAIRO544': # This cable contains a proper SUBJECT: line in some releases and in some not.
        (ur'\nBLOGGERS MOVING', u'\nSUBJECT: BLOGGERS MOVING'),
    '09CAIRO211':
        (r'''EG\nEGYPT'S 54''', u'''EG\nSUBJECT: EGYPT'S 54'''),
    '09CAIRO1468':
        (r'EG\nXXXXXXXXXXXX:', u'EG\nSUBJECT: XXXXXXXXXXXX:'),
    '09BAKU687':
        (ur'IR\nClassified By:', u'''IR
SUBJECT: IRAN: NINJA BLACK BELT MASTER DETAILS USE OF
MARTIAL ARTS CLUBS FOR REPRESSION; xxxxxxxxxxxx

REF: a) BAKU 575

Classified By:'''),
    '08KYIV2414':
        (ur'UP[ ]*\n1.', u'''UP
SUBJECT: UKRAINE: FIRTASH MAKES HIS CASE TO THE USG
REF: A. KYIV 2383 B. KYIV 2294

1.
'''),
    '09CAIRO79':
        (ur'EG\n\nClassified', u"""
SUBJECT: GOE STRUGGLING TO ADDRESS POLICE BRUTALITY

REF: A. 08 CAIRO 2431
B. 08 CAIRO 2430
C. 08 CAIRO 2260
D. 08 CAIRO 783
E. 07 CAIRO 3214
F. 07 CAIRO 2845
"""),
    '06SAOPAULO348':
        ('''BR
\(B\) Sao Paulo 215;''', u'''BR
REF: (B) Sao Paulo 215;'''),
    '09TRIPOLI63':
        ('''LY

CLASSIFIED BY:''', u'''LY

SUBJECT: RISKY BUSINESS? AMERICAN CONSTRUCTION FIRM ENTERS JOINT VENTURE WITH GOL [8466936]

CLASSIFIED BY:'''),
}

def reference_id_from_filename(filename):
    """\
    Extracts the reference identifier from the provided filename.
    """
    reference_id = os.path.basename(filename)
    if reference_id.rfind('.htm') > 0:
        reference_id = reference_id[:reference_id.rfind('.')]
    # Use the correct cable id if the reference id is malformed
    return MALFORMED_CABLE_IDS.get(reference_id, reference_id)

_REFERENCE_ID_FROM_HTML_PATTERN = re.compile('<h3>Viewing cable ([0-9]{2}[A-Z]+[0-9]+),', re.UNICODE)

def reference_id_from_html(html):
    """\
    Extracts the cable's reference identifier from the provided HTML string.

    `html`
        The HTML page of the cable.
    """
    m = _REFERENCE_ID_FROM_HTML_PATTERN.search(html)
    if m:
        return m.group(1)
    else:
        # Maybe a malformed ID?
        m = re.search(r'(%s)' % '|'.join(MALFORMED_CABLE_IDS.keys()), html, re.UNICODE)
        if m:
            return MALFORMED_CABLE_IDS[m.group(1)]
    raise ValueError("Cannot extract the cable's reference id")

def fix_content(content, reference_id):
    """\
    Fixes some oddities of cables.

    Some cables contain malformed content which is normalized here.

    This function assumes that &#x000A; has been replaced by ``\n``,
    and pilcrows, HTML links etc. have been removed (see `_clean_html`)

    The (un)changed content is returned.

    `content`
        The text content of the cable
    `reference_id`
        The reference identifier of the cable.


    >>> fix_content('\\nBLOGGERS MOVING', '09CAIRO544')
    u'\\nSUBJECT: BLOGGERS MOVING'
    >>> fix_content('\\nBLOGGERS MOVING', '09UNKNOWNID3122')
    '\\nBLOGGERS MOVING'
    """
    if reference_id in _CABLE_FIXES:
        pattern, repl = _CABLE_FIXES.get(reference_id)
        content = re.sub(pattern, repl, content)
    return content

_CONTENT_PATTERN = re.compile(ur'(?:<code><pre>)(.+?)(?:</pre></code>)', re.DOTALL|re.UNICODE)

def get_content_as_text(file_content, reference_id):
    """\
    Returns the cable content as text.

    This function removes HTML links etc. (c.f. `_clean_html`) and repairs
    the content of the cable if necessary (c.f. `fix_content`).
    
    `file_content`
        The HTML file content, c.f. `get_file_content`.
    `reference_id`
        The reference identifier of the cable.
    """
    return fix_content(_clean_html(_CONTENT_PATTERN.findall(file_content)[-1]), reference_id)

def get_header_as_text(file_content, reference_id):
    """\
    Returns the cable's header as text.
    
    `file_content`
        The HTML file content, c.f. `get_file_content`.
    """
    res = _CONTENT_PATTERN.findall(file_content)
    if len(res) == 2:
        content = res[0]
    elif len(res) == 1:
        return ''
    else:
        raise ValueError('Unexpected <code><pre> sections: "%r"' % res)
    return fix_content(_clean_html(content), reference_id)


_LINK_PATTERN = re.compile(ur'<a[^>]*>', re.UNICODE)
_HTML_TAG_PATTERN = re.compile(r'</?[a-zA-Z]+>')
_BACKSLASH_PATTERN = re.compile(r'\\[ ]*\n|\\[ ]*$')

def _clean_html(html):
    """\
    Removes links (``<a href="...">...</a>``) from the provided HTML input.
    Further, it replaces "&#x000A;" with ``\n`` and removes "¶" from the texts.
    """
    content = html.replace(u'&#x000A;', u'\n').replace(u'¶', '')
    content = _LINK_PATTERN.sub(u'', content)
    content = _HTML_TAG_PATTERN.sub(u'', content)
    content = _BACKSLASH_PATTERN.sub(u'\n', content)
    return content


_CLASSIFIED_BY_PATTERN = re.compile(r'Classified[ ]+by[^\n]+', re.IGNORECASE)
_FIRST_PARAGRAPH_PATTERN = re.compile(r'\n1. ')
_SUMMARY_PATTERN = re.compile(r'(BEGIN SUMMARY[ ])|(SUMMARY: )')

def header_body_from_content(content):
    """\
    Tries to extract the header and the message from the cable content.

    The header is something like

        UNCLASSIFIED ...
        SUBJECT ...
        REF ...

    while the message begins usually with a summary

        1. SUMMARY ...
        ...
        10. ...
    
    Returns (header, msg) or (None, None) if the header/message cannot be 
    detected.
    
    `content`
        The "content" part of a cable.
    """
    m = _CLASSIFIED_BY_PATTERN.search(content)
    idx = m and m.end() or 0
    m = _SUMMARY_PATTERN.search(content)
    summary_idx = m and m.start() or None
    m = _FIRST_PARAGRAPH_PATTERN.search(content)
    para_idx = m and m.start() or None
    if summary_idx and para_idx:
        idx = max(idx, min(summary_idx, para_idx))
    elif summary_idx:
        idx = max(summary_idx, idx)
    elif para_idx:
        idx = max(para_idx, idx)
    if idx > 0:
        return content[:idx], content[idx:]
    return None, None


_META_PATTERN = re.compile(r'''<table\s+class\s*=\s*(?:"|')cable(?:"|')\s*>.+?<td>\s*<a.+?>(.+?)</a>.+<td>\s*<a.+?>(.+?)</a>.+<td>\s*<a.+?>(.+?)</a>.+<td>\s*<a.+?>(.+?)</a>.+<td>\s*<a.+?>(.+?)</a>''', re.MULTILINE|re.DOTALL)
_MEDIA_URLS_PATTERN = re.compile(r'''<a href=(?:"|')([^"']+)''')

def parse_meta(file_content, cable):
    """\
    Extracts the reference id, date/time of creation, date/time of release,
    the classification, and the origin of the cable and assigns the values
    to the provided `cable`.
    """
    end_idx = file_content.rindex("</table>")
    start_idx = file_content.rindex("<table class='cable'>", 0, end_idx)
    m = _META_PATTERN.search(file_content, start_idx, end_idx)
    if not m:
        raise ValueError('Cable table not found')
    if len(m.groups()) != 5:
        raise ValueError('Unexpected metadata result: "%r"' % m.groups())
    # Table content: 
    # Reference ID | Created | Released | Classification | Origin
    ref, created, released, classification, origin = m.groups()
    if cable.reference_id != ref:
        reference_id = MALFORMED_CABLE_IDS.get(ref)
        if reference_id != cable.reference_id:
            raise ValueError('cable.reference_id != ref. reference_id="%s", ref="%s"' % (cable.reference_id, ref))
    cable.created = created
    cable.released = released
    cable.origin = origin
    # classifications are usually written in upper case, but you never know.. 
    cable.classification = classification.upper()
    # Try to find media IRIs
    start_idx = file_content.rfind(u'Appears in these', start_idx, end_idx)
    if start_idx > 0:
        cable.media_uris = _MEDIA_URLS_PATTERN.findall(file_content, start_idx, end_idx)
    return cable


_TID_PATTERN = re.compile(r'(VZCZ[A-Z]+[0-9]+)', re.UNICODE)

def parse_transmission_id(header, reference_id):
    """\
    Returns the transmission ID of the cable. If no transmission identifier was
    found, ``None`` is returned.

    `header`
        The cable's header
    `reference_id`
        The cable's reference ID.
    """
    m = _TID_PATTERN.search(header)
    if not m:
        return None
    return m.group(1)


_NAME2ROUTE = None

_ADDITIONAL_ROUTES = {
    'USMISSION USNATO': 'RUCNDT', # RUCNDT USMISSION USUN NEW YORK NY
    'USMISSION USUN NEW YORK': 'RUCNDT', # see above
    'SECSTATE WASHDC': 'RUEHC',
    'AMEMBASSY GUATEMALA': 'RUEHGT',
    'AMCONSUL LAGOS': 'RUEHOS',
    'AMCONSUL MELBOURNE': 'RUEHBN',
    'AMEMBASSY PANAMA': 'RUEHZP',
    'AMEMBASSY MEXICO': 'RUEHME',
    'AMEMBASSY VATICAN': 'RUEHROV',
    'AMEMBASSY ALMATY': 'RUEHTA', # Used in cables
    'AMEMBASSY QUITO': 'RUEHQT', # Used in cables 
    'AMCONSUL JOHANNESBURG': 'RUEHJO', # "RUEHJO" is used in cables
    'XMT AMCONSUL JOHANNESBURG': 'RUEHJO', #TODO: XMT?!?
    'XMT AMCONSUL STRASBOURG': 'RUEHSR', #TODO: XMT?!?
    'HQ USAFRICOM STUTTGART GE': 'RHWSAFC', # RHWSAFC STR09 SACCS USAFRICOM COMMAND CENTER STUTTGART GE
    'DEPT OF JUSTICE WASHINGTON DC': 'RUEAWJA', # RUEAWJA THRU RUEAWJD DEPT OF JUSTICE WASHINGTON DC
    'DEPARTMENT OF JUSTICE WASHINGTON DC': 'RUEAWJA', # RUEAWJA THRU RUEAWJD DEPT OF JUSTICE WASHINGTON DC
    'NATIONAL SECURITY COUNCIL WASHINGTON DC': 'RHEHNSC',
    'NSC WASHINGTON DC': 'RHEHNSC',
    'AMEMBASSY RIO DE JANEIRO': 'RUEHRI', #  AMCONSUL RIO DE JANEIRO'
    'DIA WASHINGTON DC': 'RHEFJMA', # DIA JMAS WASHINGTON DC
    'HQ USCENTCOM MACDILL AFB FL': 'RUMICEA', #TODO, see below
    'CDR USCENTCOM MACDILL AFB FL': 'RUMICEA',  #TODO: "RUMICEA" = USCENTCOM INTEL CEN MACDILL AFB FL
                                                #      "RUCQSAB" = USSOCOM INTEL MACDILL AFB FL
    'COMSOCCENT MACDILL AFB FL': 'RHMFIUU',
    'HQ USSOCOM MACDILL AFB FL': 'RHMFIUU',
    'USCINCCENT MACDILL AFB FL': 'RUMICEA',  # see above
    'USEU BRUSSELS': 'RUEHNO', # RUEHNO US MISSIONS BRUSSELS BE
    'SECDEF': 'RUEKJCS', # "RUEKJCS" is commonly used in the cables RUEKJCS/SECDEF ...
    'SECDEF WASHINGTON DC': 'RUEKJCS', # "RUEKJCS" is commonly used in the cables RUEKJCS/SECDEF ...
    'DEPT OF HOMELAND SECURITY WASHINGTON DC': 'RHEFHLC', # used in the cables: RHEFHLC/DEPT OF HOMELAND SECURITY WASHINGTON DC
    'HOMELAND SECURITY CENTER WASHINGTON DC': 'RHEFHLC',
    'USMISSION UNVIE VIENNA': 'RUEHUNV', # RUEHUNV USMISSIN UNVIE VIENNA
    'THE WHITE HOUSE WASHINGTON DC': 'RHEHAAA',
    'WHITE HOUSE WASHINGTON DC': 'RHEHAAA',
    'CJCS WASHINGTON DC': 'RUEKJCS',
    # COMUSKOREA
    'COMUSKOREA J': 'RUACAAA',
    'COMUSFK SEOUL KOR': 'RUACAAA',
    'COMUSKOREA SCJS SEOUL KOR': 'RUACAAA',
    # Collective routes extracted from other cables:
    'EUROPEAN POLITICAL COLLECTIVE': 'RUEHZL',
    'EU MEMBER STATES COLLECTIVE': 'RUCNMEM',
    'GULF COOPERATION COUNCIL COLLECTIVE': 'RUEHZM',
    'MERCOSUR COLLECTIVE': 'RUCNMER',
    'IRAN COLLECTIVE': 'RUCNIRA',
    'WESTERN HEMISPHERIC AFFAIRS DIPL POSTS': 'RUEHWH',
    'MOSCOW POLITICAL COLLECTIVE': 'RUEHXD',
    'IRAQ COLLECTIVE': 'RUCNRAQ',
    'ECOWAS COLLECTIVE': 'RUEHZK',
    'ARAB ISRAELI COLLECTIVE': 'RUEHXK',
    'ARAB LEAGUE COLLECTIVE': 'RUEHEE',
    'SOUTHERN AFRICAN DEVELOPMENT COMMUNITY': 'RUCNSAD',
    'SOUTHERN AF DEVELOPMENT COMMUNITY COLLECTIVE': 'RUCNSAD',
    'DARFUR COLLECTIVE': 'RUCNFUR',
    'AFRICAN UNION COLLECTIVE': 'RUEHZO',
    'ALL US CONSULATES IN MEXICO COLLECTIVE': 'RUEHXC',
    'OPEC COLLECTIVE': 'RUEHHH',
    'ALL NATO POST COLLECTIVE': 'RUEHXP',
    'ENVIRONMENT SCIENCE AND TECHNOLOGY COLLECTIVE': 'RUEHZN',
    'AFGHANISTAN COLLECTIVE': 'RUCNAFG',
    'WHA CENTRAL AMERICAN COLLECTIVE': 'RUEHZA',
    'UN SECURITY COUNCIL COLLECTIVE': 'RUEHGG',
    'IGAD COLLECTIVE': 'RUCNIAD',
    'DEA HQS WASHINGTON DC': 'RUEABND',
    'OSD WASHINGTON DC': 'RUEKJCS',
    'HAITI COLLECTIVE': 'RUEHZH',
    'NCTC WASHINGTON DC': 'RUEILB',
    'SOMALIA COLLECTIVE': 'RUCNSOM',
    'CDR USPACOM HONOLULU HI': 'RHHMUNA',
    'HQ USAFRICOM STUTTGART GE': 'RUEWMFD', # Also: 'HQ USAFRICOM STUTTGART GE': 'RUZEFAA',
    'CDR USAFRICOM STUTTGART GE': 'RUEWMFD', # Also: 'HQ USAFRICOM STUTTGART GE': 'RUZEFAA',
    'EUCOM POLAD VAIHINGEN GE': 'RHMCSUU',
    'HQ USEUCOM VAIHINGEN GE': 'RHMCSUU',
    'CDR USEUCOM VAIHINGEN GE': 'RHMCSUU',
    'HQ USSOUTHCOM MIAMI FL': 'RUMIAAA',
    'CDR USSOUTHCOM MIAMI FL': 'RHMFIUU',
    'RWANDA COLLECTIVE': 'RUEHXR',
    'COMNAVBASE GUANTANAMO BAY CU': 'RUCOGCA',
    'NAVINTELOFC GUANTANAMO BAY CU': 'RUCOGCA',
    'MAGHREB COLLECTIVE': 'RUCNMGH',
}

def _route_for_name(name):
    NAME2ROUTE = globals().get('_NAME2ROUTE')
    if not NAME2ROUTE:
        NAME2ROUTE = {}
        import os
        root_dir = os.path.dirname(os.path.abspath(__file__))
        f = open(root_dir + '/routes.txt')
        route_pattern = re.compile('^(R[A-Z]+)[ \t]+(.+)$')
        for l in f:
            if l.startswith('#'):
                continue
            m = route_pattern.match(l)
            NAME2ROUTE[m.group(2)] = m.group(1)
        NAME2ROUTE.update(_ADDITIONAL_ROUTES)
        globals()['_NAME2ROUTE'] = NAME2ROUTE
    res = NAME2ROUTE.get(name)
    if not res and name.endswith('WASHDC'):
        res = NAME2ROUTE.get(name.replace('WASHDC', 'WASHINGTON DC'), None)
    return res


_REC_PATTERN = re.compile(r'([A-Z]+/)?([A-Z -]{2,})(?:.*$)', re.MULTILINE|re.UNICODE)

def _route_recipient_from_header(header, reference_id):
    res = []
    for route, recipient in _REC_PATTERN.findall(header):
        if route:
            route = route.replace('/', '')
        if route == 'RHMFISS':
            route = None
        for x in ('PRIORITY', 'IMMEDIATE',
                  'NIACT', #TODO: NIght ACTion (US government immediate action security classification)
                  ):
            recipient = recipient.replace(x, '')
        if reference_id == '09BAKU179':
            recipient = recipient.replace('PIORITY', '')
        recipient = recipient.strip()
        if recipient in ('PAGE', # 08STATE23763
                         'RHMFISS', # Unclassified but Sensitive, MFI residing on the DMS NIPRNET
                         'RHMFIUU', # Secret MFI, residing on the DMS SIPRNET
                        ):
            recipient = None
        if not route and recipient:
            route = _route_for_name(recipient)
        if route or recipient:
            res.append((route, recipient))
    return res


# (?:PAGE [0-9]+ ...) was added because 09STATE15113 contains this pattern
_TO_PATTERN = re.compile(r'(?:\nTO\s+)(?:PAGE [0-9]+ [A-Z]+ [0-9]+ [0-9]+Z)?(.+?)(?=INFO|\Z)', re.DOTALL|re.UNICODE)

def parse_recipients(header, reference_id):
    """\
    Returns the recipients of the cable as (maybe empty) list.
    """
    m = _TO_PATTERN.search(header)
    if not m:
        if reference_id not in _CABLES_WITHOUT_TO:
            logger.warn('No TO header found in "%s", header: "%s"' % (reference_id, header))
        return []
    to_header = m.group(1)
    return _route_recipient_from_header(to_header, reference_id)


_INFO_PATTERN = re.compile(r'(?:\nTO\s+.+?\nINFO\s+)(.+?)(?=\Z)', re.DOTALL|re.UNICODE)

def parse_info_recipients(header, reference_id):
    """\
    Returns the informal recipients of the cable as (maybe empty) list.    
    """
    m = _INFO_PATTERN.search(header)
    if not m:
        return []
    to_header = m.group(1)
    return _route_recipient_from_header(to_header, reference_id)
    res = []
    for code, recipient in _REC_PATTERN.findall(to_header):
        for x in ('PRIORITY', 'IMMEDIATE'):
            recipient = recipient.replace(x, '')
        if reference_id == '09BAKU179':
            recipient = recipient.replace('PIORITY', '')
        recipient = recipient.strip()
        if recipient:
            # malformed cables
            if recipient == 'PAGE':
                if reference_id =='08STATE50524':
                    recipient = 'AMEMBASSY BAGHDAD'
                if reference_id == '09STATE37566':
                    recipient = None
            elif recipient == 'XMT AMCONSUL JOHANNESBURG': # '08STATE116943', '09STATE63860', 09STATE67105 
                recipient = None
            elif reference_id == '09ANKARA1594' and recipient == 'DET':
                recipient = None
            elif reference_id in ('10PRISTINA44', '10PRISTINA84') and recipient in ('RUEOBZB', 'CDR'):
                recipient = None
            elif recipient in ('RHMFISS', 'RHMFIUU'): # ANKARA cables like '07ANKARA1091', '07ANKARA1842', '07ANKARA1905', 09ANKARA1594
                recipient = None
            elif reference_id == '10SARAJEVO134' and recipient == 'XMT AMCONSUL STRASBOURG':
                recipient = 'AMCONSUL STRASBOURG'
            elif reference_id == '09PRISTINA148' and recipient == 'CDR':
                recipient = None
        if recipient:
            res.append(recipient.strip())
    return res


_SUBJECT_PATTERN = re.compile(ur'(?<!\()(?:S?UBJ(?:ECT)?(?:(?::\s*)|(?::?\s+))(?!LINE[/]*))(.+?)(?:\Z|(C O N)|(SENSI?TIVE BUT)|([ ]+REFS?:[ ]+)|(\n[ ]*\n|[\s]*[\n][\s]*[\s]*REFS?:?\s)|(REF:\s)|(REF\(S\):?)|(\s*Classified\s)|([1-9]\.?[ ]+Classified By)|([1-9]\.?[ ]*\([^\)]+\))|(1\.?[ ]Summary)|([A-Z]+\s+[0-9]+\s+[0-9]+\.?[0-9]*\s+OF)|(\-\-\-\-\-*\s+)|(Friday)|(PAGE [0-9]+)|(This is a?n Action Req))', re.DOTALL|re.IGNORECASE|re.UNICODE)
_SUBJECT_MAX_PATTERN = re.compile(r'1\.?[ ]*\([^\)]+\)')
_NL_PATTERN = re.compile(ur'[\r\n]+', re.UNICODE|re.MULTILINE)
_WS_PATTERN = re.compile(ur'[ ]{2,}', re.UNICODE)
_BRACES_PATTERN = re.compile(r'^\([^\)]+\)[ ]+| \([A-Z]+\)$')
_HTML_ENTITIES_PATTERN = re.compile(r'&#([0-9]+);')

def parse_subject(content, reference_id=None, clean=True, fix_subject=True):
    """\
    Parses and returns the subject of a cable. If the cable has no subject, an
    empty string is returned.
    
    `content`
        The cable's content.
    `reference_id`
        The (optional) reference id of the cable. Used for error msgs
    `clean`
        Indicates if classification prefixes like ``(S)`` should be removed from
        the subject (default: ``True``)
        * (TS) for Top Secret
        * (S) for Secret
        * (C) for Confidential
        * (U) for Unclassified
        * (SBU/N) for Sensitive But Unclassified/Noforn, and
        * (SBU) for Sensitive But Unclassified
        Source: 
        U.S. Department of State Foreign Affairs Handbook Volume 5 Handbook 1 — Correspondence Handbook
        5 FAH-1 H-210 -- HOW TO USE TELEGRAMS; page 2
        <http://www.state.gov/documents/organization/89319.pdf>
    `fix_subject`
        If no subject can be found in the WikiLeaks cable source, the
        subject can be set to another value if the reader has knowledge
        about the subject from 3rd party cable releases like the Aftenposten
        cable releases.
        If `fix_subject` is set to ``True`` (default) the reader tries to
        find set the subject, otherwise the subject will be an emtpy string.
    """
    def to_unicodechar(match):
        return unichr(int(match.group(1)))
    m = _SUBJECT_MAX_PATTERN.search(content)
    max_idx = m and m.start() or _MAX_HEADER_IDX
    m = _SUBJECT_PATTERN.search(content, 0, max_idx)
    if not m:
        if not fix_subject:
            return u''
        # No subject found, try to find it in the fixed subjects dict, otherwise return u''
        subject = _CABLE_SUBJECT_FIXES.get(reference_id, u'')
        if subject and clean:
            subject = _BRACES_PATTERN.sub(u'', subject)
        return subject
    res = m.group(1).strip()
    res = _NL_PATTERN.sub(u' ', res)
    res = _WS_PATTERN.sub(u' ', res)
    res = _HTML_ENTITIES_PATTERN.sub(to_unicodechar, res)
    if clean:
        res = _BRACES_PATTERN.sub(u'', res)
    return res


# Commonly month/day/year is used, but sometimes year/month/day
_DEADLINE_PATTERN = re.compile(r'(?:E.?O.?\s*12958:?\s*DECL\s*:?\s*)([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})|([0-9]{4}/[0-9]{2}/[0-9]{2})', re.IGNORECASE|re.UNICODE)

def parse_nondisclosure_deadline(content):
    """\
    Returns the non-disclosure deadline if provided.

    `content`
        The cable's content.
    """
    m = _DEADLINE_PATTERN.search(content)
    if not m:
        return None
    p1, p2 = m.groups()
    if p1:
        month, day, year = p1.split('/')
        if len(year) != 4:
            year = 2000 + int(year)
        if len(month) != 2:
            month = '0%s' % month
        if len(day) != 2:
            day = '0%s' % day
    else:
        year, month, day = p2.split('/')
    return u'%s-%s-%s' % (year, month, day)


_REF_START_PATTERN = re.compile(r'(?:[\nPROGRAM ]*REF|REF\(S\):?\s*)([^\n]+(\n\s*[0-9]+[,\s]+[^\n]+)?)', re.IGNORECASE|re.UNICODE)
_REF_LAST_REF_PATTERN = re.compile(r'(\n?[ ]*[A-Z](?:\.(?!O\.|S\.)|\))[^\n]+)', re.IGNORECASE|re.UNICODE)
_REF_PATTERN = re.compile(r'(?:[A-Z](?:\.|\))\s*)?([0-9]{2,4})?(?:\s*)([A-Z ]*[A-Z ]*[A-Z]{2,})(?:\s+)([0-9]+)', re.MULTILINE|re.UNICODE|re.IGNORECASE)
_REF_NOT_REF_PATTERN = re.compile(r'\n[0-9]\.[ ]*(?:\([A-Z]+\))?', re.IGNORECASE|re.UNICODE)
_REF_STOP_PATTERN = re.compile('classified by', re.IGNORECASE|re.UNICODE)
#TODO: The following works for all references which contain something like 02ROME1196, check with other cables
_CLEAN_REFS_PATTERN = re.compile(r'PAGE [0-9]+ [A-Z]+ [0-9]+ [0-9]+ OF [0-9]+ [A-Z0-9]+', re.UNICODE)

def parse_references(content, year, reference_id=None):
    """\
    Returns the references to other cables as (maybe empty) list.
    
    `content`
        The content of the cable.
    `year`
        The year when the cable was created.
    `reference_id`
        The reference identifier of the cable.
    """
    def format_year(y):
        y = str(y)
        if not y:
            y = str(year)
        if len(y) > 2:
            return y[2:]
        return y
    # 1. Try to find "Classified By:"
    m_stop = _REF_STOP_PATTERN.search(content)
    # If found, use it as maximum index to search for references, otherwise use a constant
    max_idx = m_stop and m_stop.start() or _MAX_HEADER_IDX
    # 2. Find references
    m_start = _REF_START_PATTERN.search(content, 0, max_idx)
    # 3. Check if we have a paragraph in the references
    m_stop = _REF_NOT_REF_PATTERN.search(content, m_start and m_start.end() or 0, max_idx)
    last_end = m_start and m_start.end() or 0
    # 4. Find the next max_idx
    max_idx = min(m_stop and m_stop.start() or _MAX_HEADER_IDX, max_idx)
    m_end = _REF_LAST_REF_PATTERN.search(content, last_end, max_idx)
    while m_end:
        last_end = m_end.end()
        m_end = _REF_LAST_REF_PATTERN.search(content, last_end, max_idx)
    res = []
    if m_end and not m_start:
        logger.warn('Found ref end but no start in "%s", content: "%s"' % (reference_id, content))
    if m_start and last_end:
        start = m_start.start(1)
        end = last_end or m_start.end()
        refs = content[start:end].replace('\n', ' ')
        refs = _CLEAN_REFS_PATTERN.sub('', refs)
        for y, origin, sn in _REF_PATTERN.findall(refs):
            y = format_year(y)
            origin = origin.replace(' ', '').upper()
            if origin in ('RIO', 'RIODEJAN'):
                origin = 'RIODEJANEIRO'
            elif origin in ('SECSTATE', 'SECDEF'):
                origin = 'STATE'
            elif origin in ('UNVIE', 'EMBASSYVIENNA'):
                origin = 'UNVIENNA'
            reference = u'%s%s%d' % (y, origin, int(sn))
            if not REFERENCE_ID_PATTERN.match(reference):
                continue
            elif reference != reference_id: 
                res.append(reference)
    return res


_TAGS_PATTERN = re.compile(r'(?:TAGS|TAG|AGS:)(?::\s*|\s+)(.+)', re.IGNORECASE|re.UNICODE)
_TAGS_SUBJECT_PATTERN = re.compile(r'(SUBJECT:)', re.IGNORECASE|re.UNICODE)
_TAGS_CONT_PATTERN = re.compile(r'(?:\n)([a-zA-Z_-]+.+)', re.MULTILINE|re.UNICODE)
_TAGS_CONT_NEXT_LINE_PATTERN = re.compile(r'\n[ ]*[A-Za-z_-]+[ ]*,', re.UNICODE)
_TAG_PATTERN = re.compile(r'(ZOELLICK[ ]+ROBERT)|(GAZA[ ]+DISENGAGEMENT)|(ISRAELI[ ]+PALESTINIAN[ ]+AFFAIRS)|(COUNTER[ ]+TERRORISM)|(CLINTON[ ]+HILLARY)|(STEINBERG[ ]+JAMES)|(BIDEN[ ]+JOSEPH)|(RICE[ ]+CONDOLEEZZA)|([A-Za-z_-]+)|(\([^\)]+\))|(?:,[ ]+)([A-Za-z_-]+[ ][A-Za-z_-]+)', re.UNICODE|re.MULTILINE)

# Used to normalize the TAG (corrects typos etc.)
_TAG_FIXES = {
    u'CLINTON HILLARY': u'CLINTON, HILLARY',
    u'STEINBERG JAMES': u'STEINBERG, JAMES B.',
    u'BIDEN JOSEPH': u'BIDEN, JOSEPH',
    u'ZOELLICK ROBERT': u'ZOELLICK, ROBERT',
    u'RICE CONDOLEEZZA': u'RICE, CONDOLEEZZA',
    u'COUNTER TERRORISM': u'COUNTERTERRORISM',
    u'MOPPS': u'MOPS', # 09BEIRUT818
    u'POGOV': u'PGOV', # 09LONDON2222
    u'RU': u'RS', # 09BERLIN1433, 09RIYADH181 etc.
    u'SYR': u'SY',
}

def parse_tags(content, reference_id=None):
    """\
    Returns the TAGS of a cable.
    
    Acc. to the U.S. SD every cable needs at least one tag.

    `content`
        The content of the cable.
    `reference_id`
        The reference identifier of the cable.
    """
    m = _TAGS_PATTERN.search(content)
    if not m:
        if reference_id not in _CABLES_WITHOUT_TAGS:
            logger.debug('No TAGS found in cable ID "%r", content: "%s"' % (reference_id, content))
        return []
    tags = m.group(1)
    min_idx = m.end()
    max_idx = _MAX_HEADER_IDX
    msubj = _TAGS_SUBJECT_PATTERN.search(tags)
    if msubj:
        tags = tags[:msubj.start()]
        max_idx = min(max_idx, msubj.start())
    m2 = None
    if tags.endswith(',') or tags.endswith(', ') or _TAGS_CONT_NEXT_LINE_PATTERN.match(content, min_idx, max_idx):
        m2 = _TAGS_CONT_PATTERN.match(content, m.end())
    if m2:
        tags = u' '.join([tags, m2.group(1)])
    res = []
    for t in _TAG_PATTERN.findall(tags):
        tag = u''.join(t).upper().replace(u')', u'').replace(u'(', u'')
        if tag == 'PTER MARR': # 07BAKU855
            res.extend(tag.split())
            continue
        elif tag == 'PHUMBA': # 08ECTION01OF02MANAMA492 which is the malformed version of 08MANAMA492
            res.extend([u'PHUM', u'BA'])
            continue
        tag = _TAG_FIXES.get(tag, tag)
        if tag not in res:
            res.append(tag)
    return res


_END_SUMMARY_PATTERN = re.compile(r'END\s+SUMMARY', re.IGNORECASE)
# 09OSLO146 contains "Summay" instead of "SummaRy"
_START_SUMMARY_PATTERN = re.compile(ur'(SUMMAR?Y( AND COMMENT)?( AND ACTION REQUEST)?( AND INTRODUCTION)?[ ‐\-\n:\.]*)', re.IGNORECASE)
# Some cables like 07BAGHDAD3895, 07TRIPOLI1066 contain "End Summary" but no "Summary:" start
# Since End Summary occurs in the first paragraph, we interpret the first paragraph as summary
_ALTERNATIVE_START_SUMMARY_PATTERN = re.compile(r'\n1\.[ ]*(\([^\)]+\))? ')
_SUMMARY_PATTERN = re.compile(r'(?:SUMMARY[ \-\n]*)(?::|\.|\s)(.+?)(?=(\n[ ]*\n)|(END[ ]+SUMMARY)|(----+))', re.DOTALL|re.IGNORECASE|re.UNICODE)
_CLEAN_SUMMARY_CLS_PATTERN = re.compile(r'^[ ]*\([SBU/NTSC]+\)[ ]*')
_CLEAN_SUMMARY_WS_PATTERN = re.compile('[ \n]+')
_CLEAN_SUMMARY_PATTERN = re.compile(r'(---+)|(((^[1-9])|(\n[1-9]))\.[ ]+\([^\)]+\)[ ]+)|(^[1-2]. Summary:)|(^[1-2]\.[ ]+)|(^and action request. )|(^and comment. )|(2. (C) Summary, continued:)', re.UNICODE|re.IGNORECASE)

def parse_summary(content, reference_id=None):
    """\
    Extracts the summary from the `content` of the cable.
    
    If no summary can be found, ``None`` is returned.
    
    `content`
        The content of the cable.
    `reference_id`
        The reference identifier of the cable.
    """
    summary = None
    m = _END_SUMMARY_PATTERN.search(content)
    if m:
        end_of_summary = m.start()
        m = _START_SUMMARY_PATTERN.search(content, 0, end_of_summary) or _ALTERNATIVE_START_SUMMARY_PATTERN.search(content, 0, end_of_summary)
        if m:
            summary = content[m.end():end_of_summary]
        elif reference_id not in _CABLES_WITH_MALFORMED_SUMMARY:
            logger.debug('Found "end of summary" but no start in "%s", content: "%s"' % (reference_id, content[:end_of_summary]))
    else:
        m = _SUMMARY_PATTERN.search(content)
        if m:
            summary = content[m.start(1):m.end(1)]
    if summary:
        summary = _CLEAN_SUMMARY_CLS_PATTERN.sub(u'', summary)
        summary = _CLEAN_SUMMARY_PATTERN.sub(u' ', summary)
        summary = _CLEAN_SUMMARY_WS_PATTERN.sub(u' ', summary)
        summary = summary.strip()
    return summary


if __name__ == '__main__':
    import doctest
    doctest.testmod()
