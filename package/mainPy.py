import gevent
import gevent.socket
import gevent.monkey
from lxml import html
from timer import Timer
from xml.dom.minidom import *
from json import JSONEncoder
from json import JSONDecoder
import xml.etree.cElementTree as ET
import requests
import sys
if 'threading' in sys.modules:
    del sys.modules['threading']


def parseData(input):
    obj = JSONDecoder().decode(input)
    pushOuput(obj)
    return obj


def formatXml():
    xmls = xml.dom.minidom.parse("filename.xml")
    pretty_xml_as_string = xmls.toprettyxml()
    outFile = open('filename.xml', 'w')
    outFile.write(pretty_xml_as_string)


def pushOuput(input):
    tree = ET.ElementTree(file='filename.xml')
    root = tree.getroot()
    bank = ET.SubElement(root, "bank")
    name = ET.SubElement(bank, "name")
    name.text = input["name"]
    link = ET.SubElement(bank, "link")
    link.text = input["link"]
    xpath = ET.SubElement(bank, "xpath")
    xpath.text = input["xpath"]
    resultQuery = ET.SubElement(bank, "resultQuery")
    resultQuery.text = input["resultQuery"]
    # wrap it in an ElementTree instance, and save as XML
    tree = ET.ElementTree(root)
    tree.write("filename.xml")


def connector(input):
    print 'Starting %s' % input
    name = input.getElementsByTagName('name')[0].firstChild.data
    print(name)
    link = input.getElementsByTagName('link')[0].firstChild.data
    xpath = input.getElementsByTagName('xpath')[0].firstChild.data
    page = requests.get(link)
    tree = html.fromstring(page.text)
    resultQuery = tree.xpath(xpath) or "null"
    jsonString = JSONEncoder().encode({
       "name": name,
       "link": link,
       "xpath": xpath,
       "resultQuery": ''.join(resultQuery).encode('ascii', 'ignore').rstrip()
    })
    parseData(jsonString)
    return jsonString


def main(input):
    root = ET.Element("html")
    tree = ET.ElementTree(root)
    tree.write("filename.xml")
    with Timer() as t:
        if input == "sync":
            banksListSource = parse('banksList.xml')
            banksList = banksListSource.getElementsByTagName('bank')
            for bank in banksList:
                name = bank.getElementsByTagName('name')[0].firstChild.data
                link = bank.getElementsByTagName('link')[0].firstChild.data
                xpath = bank.getElementsByTagName('xpath')[0].firstChild.data
                page = requests.get(link)
                tree = html.fromstring(page.text)
                resultQuery = tree.xpath(xpath)

                jsonString = JSONEncoder().encode({
                  "name": name,
                  "link": link,
                  "xpath": xpath,
                  "resultQuery": ''.join(resultQuery).encode(
                      'ascii', 'ignore'
                  ).rstrip()
                })
                parseData(jsonString)
        else:
            banksListSource = parse('banksList.xml')
            banksList = banksListSource.getElementsByTagName('bank')
            jobs = [gevent.spawn(connector, bank) for bank in banksList]
            gevent.joinall(jobs, timeout=2)
    tree = ET.ElementTree(file='filename.xml')
    root = tree.getroot()
    time = ET.SubElement(root, "time")
    time.text = str(t.secs)
    tree = ET.ElementTree(root)
    tree.write("filename.xml")
    formatXml()
    return t.secs

gevent.monkey.patch_all()
try:
    if sys.argv[1] == "sync":
        print "Synchronous:"
        main("sync")
    elif sys.argv[1] == "async":
        print "Asynchronous:"
        main("async")
    elif sys.argv[1]:
        print "wrong parameter"
except:
    print("no parameters passed")

