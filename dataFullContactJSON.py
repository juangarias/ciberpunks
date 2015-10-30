# coding=utf-8
import json


"""" JSON schema of the response
socialProfiles":
[
  {
    "typeId": {"type":"string"},
    "typeName": {"type":"string"},
    "id": {"type":"string"},
    "username": {"type":"string"},
    "url": {"type":"string"},
    "bio": {"type":"string"},
    "rss": {"type":"string"},
    "following": {"type":"number"},
    "followers": {"type":"number"}
  }
],"""


def getDataNegro():
    return json.loads("""
    {
      "status" : 200, "requestId" : "d460b77f-cf9e-4576-b534-6209304f6c8a", "likelihood" : 0.88,
      "photos" : [ {"type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
        "url" : "https://d2ojpxxtu63wzl.cloudfront.net/static/0e3bb7f79f1bb1c9653dd746a6ca0f37_ca0c4be442587a4a91067992a267dd077cb58ad1ed00f1ceaefb7e61eeae0f35",
        "isPrimary" : true
      },
      {"type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
        "url" : "http://www.linuxtopia.org/online_books/programming_books/art_of_unix_programming/graphics/kiss.png",
        "isPrimary" : true
      } ],
      "contactInfo" : {"fullName" : "Nicolás Buttarelli"  },
      "socialProfiles" : [ {
        "type" : "klout", "typeId" : "klout", "typeName" : "Klout",
        "url" : "http://klout.com/negrobuttara", "username" : "negrobuttara",
        "id" : "242912922014324395"
        }, {"followers" : 27,    "following" : 23,    "type" : "twitter",    "typeId" : "twitter",
            "typeName" : "Twitter",    "url" : "https://twitter.com/negrobuttara",    "username" : "negrobuttara",
            "id" : "384548068"
        } ],
      "digitalFootprint" : {
        "scores" : [ {"provider" : "klout",      "type" : "general",      "value" : 12
        } ],
        "topics" : [ {"provider" : "klout",      "value" : "Twitter"    },
        {"provider" : "klout",      "value" : "Politics"},
        {"provider" : "klout",      "value" : "Buenos Aires"},
        {"provider" : "klout",      "value" : "Argentina"},
        {"provider" : "klout",      "value" : "Elections"
        } ]
      }
    }""")


def getDataFeo():
    return json.loads("""{
      "status" : 200,
      "requestId" : "a900d1b5-ee80-4db3-b3c0-8507b8a6e20a",
      "likelihood" : 0.88,
      "photos" : [ {
        "type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
        "url" : "https://d2ojpxxtu63wzl.cloudfront.net/static/cba83f3b988afdccc27246d3e905727e_effd3a977b5e96e478f1f4cb949704b6253c8b3a52be70bbd468a7fa8d7cc932",
        "isPrimary" : true
      } ],
      "contactInfo" : {
        "websites" : [ {"url" : "http://www.entropeer.com"} ],
        "fullName" : "Martín Capeletto"
      },
      "socialProfiles" : [ {
        "type" : "klout", "typeId" : "klout", "typeName" : "Klout", "url" : "http://klout.com/MartinCapeletto",
        "username" : "MartinCapeletto", "id" : "26740127553517430"
      }, {
        "bio" : "Entrepreneur. Developer.\\r\\nCo-Founder of http://t.co/7fqECBm8qA and http://t.co/2H1PXnD1TZ",
        "followers" : 31, "following" : 25, "type" : "twitter", "typeId" : "twitter", "typeName" : "Twitter",
        "url" : "https://twitter.com/MartinCapeletto", "username" : "MartinCapeletto",
        "id" : "336749057"
      } ],
      "digitalFootprint" : {
        "scores" : [ {
          "provider" : "klout", "type" : "general", "value" : 31
        } ],
        "topics" : [ {"provider" : "klout", "value" : "Feedly" },
        {"provider" : "klout", "value" : "TechCrunch"},
        {"provider" : "klout", "value" : "CodeIgniter"},
        {"provider" : "klout", "value" : "Computers"},
        {"provider" : "klout","value" : "Miami"} ]
      }
    }""")
