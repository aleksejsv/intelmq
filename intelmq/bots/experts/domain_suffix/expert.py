# -*- coding: utf-8 -*-
"""
The library publicsuffixlist will be used if installed,
otherwise our own internal fallback is used.
"""
import codecs

from intelmq.lib.bot import Bot
from intelmq.lib.exceptions import InvalidArgument

try:
    from publicsuffixlist import PublicSuffixList
except ImportError:
    from .lib import PublicSuffixList


ALLOWED_FIELDS = ['fqdn', 'reverse_dns']


class DomainSuffixExpertBot(Bot):
    """Extract the domain suffix from a domain and save it in the the domain_suffix field. Requires a local file with valid domain suffixes"""
    suffixes = {}
    field: str = None
    suffix_file: str = None  # TODO: should be pathlib.Path

    def init(self):
        if self.field not in ALLOWED_FIELDS:
            raise InvalidArgument('key', got=self.field, expected=ALLOWED_FIELDS)
        with codecs.open(self.suffix_file, encoding='UTF-8') as file_handle:
            self.psl = PublicSuffixList(source=file_handle, only_icann=True)

    def process(self):
        event = self.receive_message()
        for space in ('source', 'destination'):
            key = '.'.join((space, self.field))
            if key not in event:
                continue
            event['.'.join((space, 'domain_suffix'))] = self.psl.publicsuffix(domain=event[key])

        self.send_message(event)
        self.acknowledge_message()


BOT = DomainSuffixExpertBot
