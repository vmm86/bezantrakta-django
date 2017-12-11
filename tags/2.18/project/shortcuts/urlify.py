#!/usr/bin/env python
# encoding: utf-8

import re

LATIN_MAP = {
    'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE', 'Ç':
    'C', 'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E', 'Ì': 'I', 'Í': 'I', 'Î': 'I',
    'Ï': 'I', 'Ð': 'D', 'Ñ': 'N', 'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö':
    'O', 'Ő': 'O', 'Ø': 'O', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ű': 'U',
    'Ý': 'Y', 'Þ': 'TH', 'ß': 'ss', 'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä':
    'a', 'å': 'a', 'æ': 'ae', 'ç': 'c', 'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
    'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ð': 'd', 'ñ': 'n', 'ò': 'o', 'ó':
    'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ő': 'o', 'ø': 'o', 'ù': 'u', 'ú': 'u',
    'û': 'u', 'ü': 'u', 'ű': 'u', 'ý': 'y', 'þ': 'th', 'ÿ': 'y',
}

LATIN_SYMBOLS_MAP = {
    '©': '(c)',
}

GREEK_MAP = {
    'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'h', 'θ': '8',
    'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': '3', 'ο': 'o', 'π': 'p',
    'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'y', 'φ': 'f', 'χ': 'x', 'ψ': 'ps', 'ω': 'w',
    'ά': 'a', 'έ': 'e', 'ί': 'i', 'ό': 'o', 'ύ': 'y', 'ή': 'h', 'ώ': 'w', 'ς': 's',
    'ϊ': 'i', 'ΰ': 'y', 'ϋ': 'y', 'ΐ': 'i',
    'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Θ': '8',
    'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': '3', 'Ο': 'O', 'Π': 'P',
    'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Φ': 'F', 'Χ': 'X', 'Ψ': 'PS', 'Ω': 'W',
    'Ά': 'A', 'Έ': 'E', 'Ί': 'I', 'Ό': 'O', 'Ύ': 'Y', 'Ή': 'H', 'Ώ': 'W', 'Ϊ': 'I',
    'Ϋ': 'Y',
}

TURKISH_MAP = {
    'ş': 's', 'Ş': 'S', 'ı': 'i', 'İ': 'I', 'ç': 'c', 'Ç': 'C', 'ü': 'u', 'Ü': 'U',
    'ö': 'o', 'Ö': 'O', 'ğ': 'g', 'Ğ': 'G',
}

RUSSIAN_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
    'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
    'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
    'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu',
    'Я': 'Ya',
}

UKRAINIAN_MAP = {
    'Є': 'Ye', 'І': 'I', 'Ї': 'Yi', 'Ґ': 'G', 'є': 'ye', 'і': 'i', 'ї': 'yi', 'ґ': 'g',
}

CZECH_MAP = {
    'č': 'c', 'ď': 'd', 'ě': 'e', 'ň':  'n', 'ř': 'r', 'š': 's', 'ť': 't', 'ů': 'u',
    'ž': 'z', 'Č': 'C', 'Ď': 'D', 'Ě': 'E', 'Ň':  'N', 'Ř': 'R', 'Š': 'S', 'Ť': 'T',
    'Ů': 'U', 'Ž': 'Z',
}

POLISH_MAP = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z',
    'ż': 'z', 'Ą': 'A', 'Ć': 'C', 'Ę': 'e', 'Ł': 'L', 'Ń': 'N', 'Ó': 'o', 'Ś': 'S',
    'Ź': 'Z', 'Ż': 'Z',
}

LATVIAN_MAP = {
    'ā': 'a', 'č': 'c', 'ē': 'e', 'ģ': 'g', 'ī': 'i', 'ķ': 'k', 'ļ': 'l', 'ņ': 'n',
    'š': 's', 'ū': 'u', 'ž': 'z', 'Ā': 'A', 'Č': 'C', 'Ē': 'E', 'Ģ': 'G', 'Ī': 'i',
    'Ķ': 'k', 'Ļ': 'L', 'Ņ': 'N', 'Š': 'S', 'Ū': 'u', 'Ž': 'Z',
}

ALL_DOWNCODE_MAPS = [
    LATIN_MAP,
    LATIN_SYMBOLS_MAP,
    GREEK_MAP,
    TURKISH_MAP,
    RUSSIAN_MAP,
    UKRAINIAN_MAP,
    CZECH_MAP,
    POLISH_MAP,
    LATVIAN_MAP,
]


class Downcoder:
    map = {}
    chars = ''
    for lookup in ALL_DOWNCODE_MAPS:
        for c in lookup:
            map[c] = lookup[c]
            chars += c

    regex = re.compile('[' + chars + ']|[^' + chars + ']+')


def downcode(slug):

    downcoded = ''
    pieces = Downcoder.regex.findall(slug)

    if pieces:
        for piece in pieces:
            if len(piece) == 1:
                if piece in Downcoder.map.keys():
                    downcoded += Downcoder.map[piece]
                    continue
            downcoded += piece

    else:
        downcoded = slug
    return downcoded


def urlify(s, num_chars=0):
    # remove all these words from the string before urlifying
    s = downcode(s)
    removelist = ['a', 'an', 'as', 'at', 'before', 'but', 'by', 'for', 'from',
                  'is', 'in', 'into', 'like', 'of', 'off', 'on', 'onto', 'per',
                  'since', 'than', 'the', 'this', 'that', 'to', 'up', 'via',
                  'with']

    r = re.compile(r'\b(%s)\b' % '|'.join(removelist), re.I)
    s = r.sub('', s)

    # if downcode doesn't hit, the char will be stripped here
    s = re.sub('[^-\w\s]', '', s)  # remove unneeded chars
    s = s.strip()                  # trim leading/trailing spaces
    s = re.sub('[-\s]+', '-', s)   # convert spaces to hyphens
    s = s.lower()

    # Trim the line if a character limit has been set.
    return s if not num_chars else s[:num_chars]

if __name__ == '__main__':
    print(urlify('æble   og Pære'))
