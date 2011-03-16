#!/usr/bin/env python
# -*- coding: utf-8 -*-

from saml2 import BINDING_HTTP_REDIRECT, BINDING_SOAP, BINDING_HTTP_POST
from saml2.config import SPConfig, IdPConfig, Config
from saml2.metadata import MetaData
from py.test import raises

sp1 = {
    "entityid" : "urn:mace:umu.se:saml:roland:sp",
    "endpoints" : {
        "assertion_consumer_service" : ["http://lingon.catalogix.se:8087/"],
    },
    "name": "test",
    "idp" : {
        "urn:mace:example.com:saml:roland:idp": {'single_sign_on_service':
        {'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
         'http://localhost:8088/sso/'}},
    },
    "key_file" : "mykey.pem",
    "cert_file" : "mycert.pem",
    "xmlsec_binary" : "/opt/local/bin/xmlsec1",
    "metadata": { 
        "local": ["metadata.xml", 
                    "urn-mace-swami.se-swamid-test-1.0-metadata.xml"],
    },
    "virtual_organization" : {
        "coip":{
            "nameid_format" : "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
            "common_identifier": "eduPersonPrincipalName",
            "attribute_auth": [
                "https://coip-test.sunet.se/idp/shibboleth",
            ]
        }
    },
    "attribute_map_dir": "attributemaps"
}

sp2 = {
    "entityid" : "urn:mace:umu.se:saml:roland:sp",
    "name" : "Rolands SP",
    "endpoints" : {
        "assertion_consumer_service" : ["http://lingon.catalogix.se:8087/"],
    },
    "required_attributes": ["surName", "givenName", "mail"],
    "optional_attributes": ["title"],
    "idp": {
        "" : "https://example.com/saml2/idp/SSOService.php",
    },
    "xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

IDP1 = {
    "entityid" : "urn:mace:umu.se:saml:roland:idp",
    "name" : "Rolands IdP",
    "endpoints": {
        "single_sign_on_service" : ["http://localhost:8088/"],
    },
    "policy": {
        "default": {
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "eduPersonAffiliation": ["(member|staff)"],
                "mail": [".*@example.com"],
            }
        },
        "urn:mace:umu.se:saml:roland:sp": None
    },
    "xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

IDP2 = {
    "entityid" : "urn:mace:umu.se:saml:roland:idp",
    "name" : "Rolands IdP",
    "endpoints": {
        "single_sign_on_service" : ["http://localhost:8088/"],
        "single_logout_service" : [("http://localhost:8088/", BINDING_HTTP_REDIRECT)],
    },
    "policy":{
        "default": {
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "eduPersonAffiliation": ["(member|staff)"],
                "mail": [".*@example.com"],
            }
        },
        "urn:mace:umu.se:saml:roland:sp": None
    },
    "xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

def _eq(l1,l2):
    return set(l1) == set(l2)

def test_1():
    c = SPConfig().load(sp1)
    
    print c
    assert c.endpoints
    assert c.name
    assert c.idp
    md = c.metadata
    assert isinstance(md, MetaData)

    assert len(c.idp) == 1
    assert c.idp.keys() == ["urn:mace:example.com:saml:roland:idp"]
    assert c.idp.values() == [{'single_sign_on_service':
        {'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
         'http://localhost:8088/sso/'}}]

def test_2():
    c = SPConfig().load(sp2)
    
    print c
    assert c.endpoints
    assert c.idp
    assert c.optional_attributes
    assert c.name
    assert c.required_attributes

    assert len(c.idp) == 1
    assert c.idp.keys() == [""]
    assert c.idp.values() == ["https://example.com/saml2/idp/SSOService.php"]

    
def test_minimum():
    minimum = {
        "entityid" : "urn:mace:example.com:saml:roland:sp",
        "endpoints" : {
            "assertion_consumer_service" : ["http://sp.example.org/"],
        },
        "name" : "test",
        "idp": {
            "" : "https://example.com/idp/SSOService.php",
        },
        "xmlsec_binary" : "/usr/local/bin/xmlsec1",
    }

    c = SPConfig().load(minimum)
    
    assert c != None
    
def test_idp_1():
    c = IdPConfig().load(IDP1)
    
    print c
    assert c.endpoint("single_sign_on_service") == 'http://localhost:8088/'

    attribute_restrictions = c.policy.get_attribute_restriction("")
    assert attribute_restrictions["eduPersonAffiliation"][0].match("staff")

def test_idp_2():
    c = IdPConfig().load(IDP2)

    print c
    assert c.endpoint("single_logout_service",
                      BINDING_SOAP) == None
    assert c.endpoint("single_logout_service",
                        BINDING_HTTP_REDIRECT) == 'http://localhost:8088/'

    attribute_restrictions = c.policy.get_attribute_restriction("")
    assert attribute_restrictions["eduPersonAffiliation"][0].match("staff")
    
def test_wayf():
    c = SPConfig().load_file("server.config")
    
    idps = c.idps()
    assert idps == {'urn:mace:example.com:saml:roland:idp': 'Example Co.'}
    idps = c.idps(["se","en"])
    assert idps == {'urn:mace:example.com:saml:roland:idp': 'Exempel AB'}

def test_3():
    cnf = Config()
    cnf.load_file("sp_1.conf")
    assert cnf.entityid == "urn:mace:example.com:saml:roland:sp"
    assert cnf.debug == 1
    assert cnf.key_file == "test.key"
    assert cnf.cert_file == "test.pem"
    assert cnf.xmlsec_binary ==  "/usr/local/bin/xmlsec1"
    assert cnf.accepted_time_diff == 60
    assert cnf.secret == "0123456789"
    assert cnf.metadata is not None
    assert cnf.attribute_converters is not None

def test_sp():
    cnf = SPConfig()
    cnf.load_file("sp_1.conf")
    assert cnf.single_logout_services("urn:mace:example.com:saml:roland:idp",
                            BINDING_HTTP_POST) == ["http://localhost:8088/slo"]
    assert cnf.endpoint("assertion_consumer_service") == \
                                            "http://lingon.catalogix.se:8087/"
    assert len(cnf.idps()) == 1