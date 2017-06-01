import datetime
import subprocess
import sys
import time
from datetime import date

from OpenSSL import crypto
from six import string_types

from eu.softfire.pd.utils.utils import get_config

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


def bytes_compat(string, encoding='utf-8'):
    if sys.version_info.major >= 3:
        if not isinstance(string, string_types):
            string = str(string)
        return bytes(string, encoding)
    else:
        return bytes(string)


class CertificateGenerator(object):
    def __init__(self, username):
        self.key_length = '2048'
        self.serial_number = time.time().as_integer_ratio()[0]
        # self.digest = 'sha256WithRSAEncryption'
        self.digest = 'sha1'
        with open(get_config('system', 'cert-ca-file', '/etc/softfire/softfire-ca.p12'), 'rb') as buf:
            buffer = buf.read()
            load_pkcs_ = crypto.load_pkcs12(buffer=buffer,
                                            passphrase=get_config('system', 'cert-passphrase', 'softfire'))
            self.ca_cert = load_pkcs_.get_certificate()
            self.ca_key = load_pkcs_.get_privatekey()

        d = date.today()
        self.validity_start = datetime.datetime.combine(d, datetime.datetime.min.time())
        d = d + datetime.timedelta(days=DEFAULT_CERT_VALIDITY)
        self.validity_end = datetime.datetime.combine(d, datetime.datetime.min.time())
        self.certificate = None
        self.private_key = None
        self.country_code = 'DE'
        self.common_name = username
        self.organization = 'SoftFIRE'

    def generate(self):
        """
        (internal use only)
        generates a new x509 certificate (CA or end-entity)
        """
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, int(self.key_length))
        cert = crypto.X509()
        subject = self._fill_subject(cert.get_subject())

        cert.set_version(0x2)  # version 3 (0 indexed counting)
        cert.set_subject(subject)
        cert.set_serial_number(self.serial_number)
        start_strftime = self.validity_start.strftime(generalized_time)
        end_strftime = self.validity_end.strftime(generalized_time)

        cert.set_notBefore(bytes_compat(start_strftime))
        cert.set_notAfter(bytes_compat(end_strftime))

        issuer = self.ca_cert.get_subject()
        issuer_key = self.ca_key
        cert.set_issuer(issuer)

        cert.set_pubkey(key)
        cert = self._add_extensions(cert)
        cert.sign(issuer_key, str(self.digest))

        self.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        self.private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)


    def _fill_subject(self, subject):
        """
        (internal use only)
        fills OpenSSL.crypto.X509Name object
        """

        attr_map = {
            'country_code': 'countryName',
            # 'state': 'stateOrProvinceName',
            # 'city': 'localityName',
            'organization': 'organizationName',
            # 'email': 'emailAddress',
            'common_name': 'commonName'
        }  # set x509 subject attributes only if not empty strings
        for model_attr, subject_attr in attr_map.items():
            value = getattr(self, model_attr)
            if value:
                # coerce value to string, allow these fields to be redefined
                # as foreign keys by subclasses without losing compatibility
                if not isinstance(value, string_types):
                    value = str(value)
                setattr(subject, subject_attr, value)
        return subject

    def _add_extensions(self, cert):
        """
        (internal use only)
        adds x509 extensions to ``cert``
        """
        ext = list()

        # prepare extensions for end-entity certs
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
        # authorityKeyIdentifier must be added after
        # the other extensions have been already added
        cert.add_extensions([
            crypto.X509Extension(b'authorityKeyIdentifier',
                                 False,
                                 b'keyid:always,issuer:always',
                                 issuer=issuer_cert)
        ])
        # for ext in self.extensions:
        #     cert.add_extensions([
        #         crypto.X509Extension(bytes_compat(ext['name']),
        #                              bool(ext['critical']),
        #                              bytes_compat(ext['value']))
        #     ])
        return cert


if __name__ == '__main__':
    cert_gen = CertificateGenerator('user_number_1')
    cert_gen.generate()
    print("""
dev tun
client
remote softfire-vpn.av.tu-berlin.de 443
;proto udp
proto tcp
nobind
persist-key
persist-tun
comp-lzo
keepalive 10 120
verb 3
remote-cert-tls server
resolv-retry infinite
nobind
<ca>
-----BEGIN CERTIFICATE-----
MIIFAzCCA+ugAwIBAgIQLJdZE0PTZ7/N1PiCOH1EOzANBgkqhkiG9w0BAQsFADCB
pTELMAkGA1UEBhMCREUxDzANBgNVBAgMBkJlcmxpbjEPMA0GA1UEBwwGQmVybGlu
MRIwEAYDVQQKDAlUVSBCZXJsaW4xCzAJBgNVBAsMAkFWMR4wHAYDVQQDDBVUVSBC
ZXJsaW4gU29mdEZJUkUgQ0ExMzAxBgkqhkiG9w0BCQEWJGF2LWluZnJhc3RydWN0
dXJlQGxpc3RzLnR1LWJlcmxpbi5kZTAeFw0xNjA2MjcxNTMxNTlaFw0yMTA2MjYx
NTMxNTlaMIGlMQswCQYDVQQGEwJERTEPMA0GA1UECAwGQmVybGluMQ8wDQYDVQQH
DAZCZXJsaW4xEjAQBgNVBAoMCVRVIEJlcmxpbjELMAkGA1UECwwCQVYxHjAcBgNV
BAMMFVRVIEJlcmxpbiBTb2Z0RklSRSBDQTEzMDEGCSqGSIb3DQEJARYkYXYtaW5m
cmFzdHJ1Y3R1cmVAbGlzdHMudHUtYmVybGluLmRlMIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEA1Fk2hti4hsahT8t+8fEfxrSAiJJDuXyj5g48mn37u8o2
0VK/9STmG7nCiZQwtEIiz9MpxDo6oeap8qwJacp5V6RTZ5d3sPypfM5S06vxTOZX
KsvWWv7E7An+O0J8I819mfg3/SkJJmu12i13f+r03+29hnlPZaXuqZnQmKFfolpP
GHTaPLbn5aED17Lyg0eyFiCCXBes5FM9fBuqbSU+jDmfwd+nBcJG61oHdrGvp5vZ
gUQm8X43sMeb/dP8ncHP3cft47A5QHc+GKDNroWW43almezOgByzzckG39eWqV0h
E18Bts5y9BUdsYNJdZaLEWAPMLR8Li3LAx1gd2YVwQIDAQABo4IBKzCCAScwEgYD
VR0TAQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYEFDMfaUfm
l6CQdssrpTLv4WG81BHhMIHhBgNVHSMEgdkwgdaAFDMfaUfml6CQdssrpTLv4WG8
1BHhoYGrpIGoMIGlMQswCQYDVQQGEwJERTEPMA0GA1UECAwGQmVybGluMQ8wDQYD
VQQHDAZCZXJsaW4xEjAQBgNVBAoMCVRVIEJlcmxpbjELMAkGA1UECwwCQVYxHjAc
BgNVBAMMFVRVIEJlcmxpbiBTb2Z0RklSRSBDQTEzMDEGCSqGSIb3DQEJARYkYXYt
aW5mcmFzdHJ1Y3R1cmVAbGlzdHMudHUtYmVybGluLmRlghAsl1kTQ9Nnv83U+II4
fUQ7MA0GCSqGSIb3DQEBCwUAA4IBAQCz6j6JMXbBUG0j4Ijx4JsuuuHaJBmBB/eN
S6qthzg8F6wC45K2Xel0T3+uhFmnBbylWIVP0Xl3SthGeukJqT2VgnbRbYt6I17x
ot8eUyZb495moDJ8wWN8XU6Atcl6igB2tNmsZkj5OnaepQTyy1Ocl8akHN4TNKD5
olNy0TpH70+FfzuDRKGqfzivAT5P3l1zyRcRDSk4wVEXFB/95ZqX90AvPiLOfGAe
aEIbwcXwcVxYma83LhCiBZo3SQ1wH+cvOrDwQ/SY0u2fndpf5WqAeBj9A3aYgqCS
lMg366OjDzFpNaTLX4HQPX682AuMj338NPLoPXXfyHxmIMN4ZRcs
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFmTCCBIGgAwIBAgICAQIwDQYJKoZIhvcNAQELBQAwgaUxCzAJBgNVBAYTAkRF
MQ8wDQYDVQQIDAZCZXJsaW4xDzANBgNVBAcMBkJlcmxpbjESMBAGA1UECgwJVFUg
QmVybGluMQswCQYDVQQLDAJBVjEeMBwGA1UEAwwVVFUgQmVybGluIFNvZnRGSVJF
IENBMTMwMQYJKoZIhvcNAQkBFiRhdi1pbmZyYXN0cnVjdHVyZUBsaXN0cy50dS1i
ZXJsaW4uZGUwHhcNMTYwNzI3MTQ0ODQzWhcNMTgwNzI3MTQ0ODQzWjBgMQswCQYD
VQQGEwJERTEPMA0GA1UECAwGQmVybGluMQ8wDQYDVQQHDAZCZXJsaW4xGTAXBgNV
BAoMEEZyYXVuaG9mZXIgRk9LVVMxFDASBgNVBAMMC0ZpdGVhZ2xlIENBMIICIjAN
BgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA3Hy2l7zLZRE306xu15X9jZFub7SS
yiQxndC4zDun+av/TiQJU/gK1/TPo6Y0u2+sqpuTPCh6XBA2N63AmZzpZpSAMBux
JTm+BOYIqa0GJ5tW5tKBMPH3pITdgsh256ckyf57LUKH66yQgTfJskpF5ovDMNUq
6vZAvEVjXa/A3tUaB5NxcQeLixKJJrmuh2TBxN3OOWNKD8vyal6KKOTYpeaillZ9
zqmtNr9nXnlhfMBZPXJBQmw2OOlaX5uIuceMkpg6TIVrNlbdJuS9TeTVmx1MtmVm
73Q5ii2FcopYrV1v8W4C3atxFCTfmFRlrRm6sJ7ZRQhGtJphPZczwtqcC7MKJjQN
bYeAG8BQHRnVQrVXr5+jrysqFWGoXGDISVprm0DjGij5ok2jIYaSgBpLVrD3e4eC
LgYH58+f8u5tQxE1TxGCudAb0fSMy+GAe+5qbbEQkLc/+WXnGi4xTTozebmccJs8
mbu5/BICYu5e53B58DFJy8x8qjLQjXuvspKqcPT5Dp07LmIu30sgrXG+Mdq1cWjV
VHx9XwJz1c89Oy/6TandrznRfGVNAzXPenm3gr0wib7qwWlsSPTrBOcXyjMthV27
wX6MK5GWWH+Uk5Z9a/V2JE9+J3KtEtk8D4xSEIQJ+pJZtXh1YxNzzYhY/czJLYdA
loVSHOjwDmPtbEECAwEAAaOCARUwggERMAwGA1UdEwQFMAMBAf8wHQYDVR0OBBYE
FMKA1MAJkTlwFZ5USVhoOJkZO4CDMIHhBgNVHSMEgdkwgdaAFDMfaUfml6CQdssr
pTLv4WG81BHhoYGrpIGoMIGlMQswCQYDVQQGEwJERTEPMA0GA1UECAwGQmVybGlu
MQ8wDQYDVQQHDAZCZXJsaW4xEjAQBgNVBAoMCVRVIEJlcmxpbjELMAkGA1UECwwC
QVYxHjAcBgNVBAMMFVRVIEJlcmxpbiBTb2Z0RklSRSBDQTEzMDEGCSqGSIb3DQEJ
ARYkYXYtaW5mcmFzdHJ1Y3R1cmVAbGlzdHMudHUtYmVybGluLmRlghAsl1kTQ9Nn
v83U+II4fUQ7MA0GCSqGSIb3DQEBCwUAA4IBAQAYcCmGctVfnRZ6oL2z6qvn9Dhm
Hpt1zIC0pR7vKroi8OyGpv+BB7gHEXX0ecq8VtLKTcXWYR+7NdZS7IX8lyd81LiX
XB1x09hEKH8O71T9v3TAMVtFDHmUito8cJQtPJFlVLZyL5xF+H0VHHEED4JP8xp4
KPFd2Rt0ixTNnE3ccUgumty1X+xq0rWSCzOXy11TxOv2tzB7TA/O85XRw9QzE3jw
4WjTS7tH9Phe/JTxbnhADS7k5mHZ+FDmX4xeTrXKNKv9+W1Qz9qQQ441IWpokBow
tBeOMiadvRRQ2fhNuKCpgVUgyUyts0fFvDwJhLTnUqEbdgr19HbLO8GwqPbk
-----END CERTIFICATE-----
</ca>
<cert>""")
    print(cert_gen.certificate.decode("utf-8") + "</cert>\n<key>")
    print(cert_gen.private_key.decode("utf-8") + "</key>")
    print("")
    print("")
    print("")
    print("")

    output = subprocess.check_output(['openssl', 'x509', '-noout', '-text'], input=cert_gen.certificate).decode('utf-8')
    print(output)
