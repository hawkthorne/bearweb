import json

from django.test import TestCase

from games import fieldmarshal
from games.fieldmarshal import Struct
from games.api import MetricContainer


class Foo(Struct):
    id = unicode


class Bar(Struct):
    id = bool


class Baz(Struct):
    id = int


class Bap(Struct):
    id = None


class Nested(Struct):
    foo = Foo


class SuperNested(Struct):
    nested = Nested


class ArrayFoo(Struct):
    foos = [Foo]


class HashFoo(Struct):
    foos = {}


class FieldMarshalTest(TestCase):

    def test_array(self):
        c = ArrayFoo()
        self.assertEquals(len(c.foos), 0)

    def test_hash(self):
        c = HashFoo()
        self.assertEquals(c.foos.items(), [])

    def test_recursive_dumps(self):
        c = Nested(foo=Foo(id=u"foo"))
        self.assertEquals(fieldmarshal.dumps(c),
                          json.dumps({"foo": {"id": "foo"}}))

    def test_recursive_load(self):
        resp = json.dumps({"foo": {"id": "foo"}})
        c = fieldmarshal.loads(Nested, resp)
        self.assertEquals(c.foo.id, "foo")

    def test_deeper_load(self):
        resp = json.dumps({"nested": {"foo": {"id": "foo"}}})
        c = fieldmarshal.loads(SuperNested, resp)
        self.assertEquals(c.nested.foo.id, "foo")

    def test_dumps(self):
        c = Foo(id=u"foo")
        self.assertEquals(fieldmarshal.dumps(c),
                          json.dumps({"id": "foo"}))

    def test_dumpd(self):
        c = Foo(id=u"foo")
        self.assertEquals(fieldmarshal.dumpd(c),
                          {u"id": u"foo"})

    def test_zero_value_string(self):
        c = Foo()
        self.assertEquals(c.id, "")

    def test_zero_value_none(self):
        c = Bap()
        self.assertEquals(c.id, None)

    def test_zero_value_bool(self):
        c = Bar()
        self.assertEquals(c.id, False)

    def test_zero_value_int(self):
        c = Baz()
        self.assertEquals(c.id, 0)

    def test_zero_value_struct(self):
        c = Nested()
        self.assertEquals(c.foo.id, "")

    def test_loads(self):
        resp = json.dumps({"id": "foo"})
        c = fieldmarshal.loads(Foo, resp)
        self.assertEquals(c.id, "foo")

    def test_loads_wrong_value(self):

        class Number(Struct):
            id = int

        resp = json.dumps({"id": "foo"})

        with self.assertRaises(ValueError):
            fieldmarshal.loads(Number, resp)

    def test_bearraid_metrics(self):
        resp = {
            'metrics': [{
                'event': 'open',
                'properties': {
                    'foo': 'bar',
                },
            }],
        }

        p = fieldmarshal.loads(MetricContainer, json.dumps(resp))

        m = p.metrics[0]

        self.assertEquals('open', m.event)
        self.assertEquals('bar', m.properties['foo'])

    def test_bearraid_metrics_bad_type(self):
        resp = {
            'metrics': [{
                'event': 3,
                'properties': {
                    'foo': 'bar',
                },
            }],
        }

        with self.assertRaises(ValueError):
            fieldmarshal.loads(MetricContainer, json.dumps(resp))
