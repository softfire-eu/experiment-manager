import datetime
import random
import subprocess
import sys

from OpenSSL import crypto
from bottle import template
from six import string_types

from eu.softfire.tub.utils.utils import get_config, get_logger

KEY_LENGTH_CHOICES = {
    'none': ('', ''),
    '512': ('512', '512'),
    '1024': ('1024', '1024'),
    '2048': ('2048', '2048'),
    '4096': ('4096', '4096')
}

DEFAULT_CERT_VALIDITY = 1
DEFAULT_KEY_LENGTH = '2048'
DEFAULT_DIGEST_ALGORITHM = 'sha256'
CERT_KEYUSAGE_CRITICAL = False
CERT_KEYUSAGE_VALUE = 'digitalSignature, keyEncipherment'
CRL_PROTECTED = False

generalized_time = '%Y%m%d%H%M%SZ'
logger = get_logger(__name__)


def bytes_compat(string, encoding='utf-8'):
    if sys.version_info.major >= 3:
        if not isinstance(string, string_types):
            string = str(string)
        return bytes(string, encoding)
    else:
        return bytes(string)


class CertificateGenerator(object):
    def __init__(self):
        self.key_length = 2048
        self.digest = 'sha1'
        with open(get_config('system', 'cert-ca-file', '/etc/softfire/softfire-ca.p12'), 'rb') as buf:
            buffer = buf.read()
        load_pkcs_ = crypto.load_pkcs12(buffer=buffer,
                                        passphrase=get_config('system', 'cert-passphrase', 'softfire').encode())
        self.ca_cert = load_pkcs_.get_certificate()
        self.ca_key = load_pkcs_.get_privatekey()
        self.certificate = None
        self.private_key = None
        with open(get_config('system', 'openvpn-template-location', '/etc/softfire/template_openvpn.tpl'), 'r') as f:
            self.openvpn_config_tpl = f.read()

    def generate(self, passphrase: str = None, common_name=None, days=DEFAULT_CERT_VALIDITY):
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, self.key_length)

        cert = crypto.X509()
        # cert.get_subject().CN = common_name
        cert.get_subject().commonName = common_name
        cert.set_serial_number(random.randint(990000, 999999999999999999999999999))
        cert.gmtime_adj_notBefore(-600)
        cert.gmtime_adj_notAfter(int(datetime.timedelta(days=days).total_seconds()))
        cert.set_issuer(self.ca_cert.get_subject())
        cert.set_pubkey(k)
        cert = self._add_extensions(cert)
        cert.sign(self.ca_key, self.digest)

        self.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        self.private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, k, cipher="DES-EDE3-CBC", passphrase=passphrase.encode())
        return self

    def _add_extensions(self, cert):
        """
        (internal use only)
        adds x509 extensions to ``cert``
        """
        ext = list()
        ext.append(crypto.X509Extension(b'basicConstraints',
                                        True,
                                        b'CA:FALSE'))
        ext.append(crypto.X509Extension(b'keyUsage',
                                        CERT_KEYUSAGE_CRITICAL,
                                        bytes_compat(CERT_KEYUSAGE_VALUE)))
        issuer_cert = self.ca_cert
        ext.append(crypto.X509Extension(b'subjectKeyIdentifier',
                                        False,
                                        b'hash',
                                        subject=cert))
        cert.add_extensions(ext)
        cert.add_extensions([
            crypto.X509Extension(b'authorityKeyIdentifier',
                                 False,
                                 b'keyid:always,issuer:always',
                                 issuer=issuer_cert)
        ])
        return cert

    def get_openvpn_config(self):
        openvpn_options = {
            'openvpn_server': get_config('openvpn', 'openvpn_server', 'softfire-vpn.av.tu-berlin.de'),
            'openvpn_port': int(get_config('openvpn', 'openvpn_port', "443")),
            'protocol': get_config('openvpn', 'openvpn_protocol', 'tcp'),
            'certificate': self.certificate.decode("utf-8"), 'key': self.private_key.decode("utf-8")
        }
        return template(self.openvpn_config_tpl, openvpn_options)


if __name__ == '__main__':
    cert_gen = CertificateGenerator()
    cert_gen.generate(passphrase='123456', common_name="foobar", days=1)
    print(cert_gen.get_openvpn_config())
    print("")
    print("")
    print("")
    print("")

    output = subprocess.check_output(['openssl', 'x509', '-noout', '-text'], input=cert_gen.certificate).decode('utf-8')
    print(output)
