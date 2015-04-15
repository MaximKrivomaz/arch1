import unittest
from mainPy import main, connector, parseData
from xml.dom.minidom import *
from json import JSONEncoder
from json import JSONDecoder


class TestFactorial(unittest.TestCase):
    def test_main(self):
        self.assertIsInstance(main("sync"), float, "Sync main returned not float")
        self.assertIsInstance(main("async"), float, "Async main returned not float")
        self.assertGreater(main("sync"), main("async"), "Async func worked longer than sync")

    def test_connector(self):
        str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><list><name>myName</name><link>http://test.com</link><xpath>myXpath</xpath></list>"
        buf = JSONEncoder().encode({
            "name": "myName",
            "link": "http://test.com",
            "xpath": "myXpath",
            "resultQuery": "null"
        })
        self.assertEqual(connector(parseString(str)), buf, "Connector returned wrong json data")

    def test_parse_data(self):
        buf = JSONEncoder().encode({
            "name": "myName",
            "link": "http://test.com",
            "xpath": "myXpath",
            "resultQuery": "null"
        })
        self.assertIsInstance(parseData(buf), object, "JSON-string was not parsed")
if __name__ == '__main__':
    unittest.main()