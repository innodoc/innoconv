# pylint: disable=missing-docstring

import unittest
import panflute as pf

from innoconv.ifttm_filter.filter_action import IfttmFilterAction


class TestFilterAction(unittest.TestCase):
    def test_ifttm_block_fi_else_fi(self):
        """filter() should handle block if/else/fi"""
        filter_action = IfttmFilterAction()
        doc = pf.Doc()
        blocks = [
            pf.RawBlock(r'\ifttm', format='latex'),
            pf.Para(pf.Str('foo')),
            pf.RawBlock(r'\else', format='latex'),
            pf.Para(pf.Str('bar')),
            pf.RawBlock(r'\fi', format='latex'),
        ]
        doc.content.extend(blocks)

        with self.subTest('handle ifttm'):
            elem = doc.content[0]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle para foo'):
            elem = doc.content[1]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle else'):
            elem = doc.content[2]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle para bar'):
            elem = doc.content[3]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle fi'):
            elem = doc.content[4]
            ret = filter_action.filter(elem, elem.doc)[0]
            self.assertIsInstance(ret, pf.Para)
            self.assertIsInstance(ret.content[0], pf.Str)
            self.assertEqual(ret.content[0].text, 'foo')

    def test_ifttm_block_if_fi(self):
        """filter() should handle block if/fi"""
        filter_action = IfttmFilterAction()
        doc = pf.Doc()
        blocks = [
            pf.RawBlock(r'\ifttm', format='latex'),
            pf.Para(pf.Str('foo')),
            pf.RawBlock(r'\fi', format='latex'),
        ]
        doc.content.extend(blocks)

        with self.subTest('handle ifttm'):
            elem = doc.content[0]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle para foo'):
            elem = doc.content[1]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle fi'):
            elem = doc.content[2]
            ret = filter_action.filter(elem, elem.doc)[0]
            self.assertIsInstance(ret, pf.Para)
            self.assertIsInstance(ret.content[0], pf.Str)
            self.assertEqual(ret.content[0].text, 'foo')

    def test_ifttm_inline_if_else_fi(self):
        """filter() should handle inline if/else/fi"""
        filter_action = IfttmFilterAction()
        doc = pf.Doc()
        blocks = [
            pf.Para(
                pf.RawInline(r'\ifttm', format='latex'),
                pf.Str('foo'),
                pf.RawInline(r'\else', format='latex'),
                pf.Str('bar'),
                pf.RawInline(r'\fi', format='latex'),
            )
        ]
        doc.content.extend(blocks)
        para = doc.content[0]

        with self.subTest('handle ifttm'):
            elem = para.content[0]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest("handle Str('foo')"):
            elem = para.content[1]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle else'):
            elem = para.content[2]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest("handle Str('bar')"):
            elem = para.content[3]
            ret = filter_action.filter(elem, elem.doc)
            self.assertEqual(ret, [])

        with self.subTest('handle fi'):
            elem = para.content[4]
            ret = filter_action.filter(elem, elem.doc)[0]
            self.assertIsInstance(ret, pf.Str)
            self.assertEqual(ret.text, 'foo')

    def test_invalid_value_elem(self):
        """filter() raises ValueError if elem=None"""
        filter_action = IfttmFilterAction()
        with self.assertRaises(ValueError):
            filter_action.filter(None, pf.Doc())

    def test_invalid_value_doc(self):
        """filter() raises ValueError if doc=None"""
        filter_action = IfttmFilterAction()
        with self.assertRaises(ValueError):
            filter_action.filter(pf.Para(), None)

    def test_str_untouched(self):
        """filter() should not change pf.Str"""
        filter_action = IfttmFilterAction()
        doc = pf.Doc()
        elem = pf.Str('foo')
        blocks = [pf.Para(elem)]
        doc.content.extend(blocks)
        ret = filter_action.filter(str, pf.Doc())
        self.assertIsNone(ret)


class TestFilterActionClean(unittest.TestCase):

    # pylint: disable=protected-access

    def test_clean_empty(self):
        """_clean() should return [] if given []"""
        filter_action = IfttmFilterAction()
        ret = filter_action._clean([], pf.Str('foo'))
        self.assertListEqual(ret, [])

    def test_clean_remove_empty_paras(self):
        r"""_clean() should remove empty paras in list"""
        filter_action = IfttmFilterAction()
        elems = [pf.Str('foo'), pf.Para()]
        ret = filter_action._clean(elems, pf.RawInline(r'\fi'))
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0].text, 'foo')

    def test_clean_wrap_inlines(self):
        r"""_clean() should wrap inlines if closing \fi is RawBlock"""
        filter_action = IfttmFilterAction()
        elems = [pf.Str('foo'), pf.Space(), pf.Str('bar')]
        ret = filter_action._clean(elems, pf.RawBlock(r'\fi'))
        self.assertEqual(len(ret), 1)
        self.assertEqual(len(ret[0].content), 3)
        self.assertEqual(ret[0].content[0].text, 'foo')
        self.assertIsInstance(ret[0].content[1], pf.Space)
        self.assertEqual(ret[0].content[2].text, 'bar')

    def test_clean_unwrap_para(self):
        r"""_clean() should unwrap a para if closing \fi is RawInline"""
        filter_action = IfttmFilterAction()
        elems = [pf.Para(pf.Str('foo'), pf.Space(), pf.Str('bar'))]
        ret = filter_action._clean(elems, pf.RawInline(r'\fi'))
        self.assertEqual(len(ret), 3)
        self.assertEqual(getattr(ret[0], 'text'), 'foo')
        self.assertIsInstance(ret[1], pf.Space)
        self.assertEqual(ret[2].text, 'bar')
