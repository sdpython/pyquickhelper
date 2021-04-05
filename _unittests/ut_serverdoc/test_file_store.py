"""
@brief      test log(time=1s)

"""
import unittest
import os
import pandas
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.server.filestore_sqlite import SqlLite3FileStore


class TestfileStore(ExtTestCase):

    def test_file_store(self):
        temp = get_temp_folder(__file__, "temp_file_storage")
        name = os.path.join(temp, "filestore.db3")
        store = SqlLite3FileStore(name)
        df = pandas.DataFrame({"A": ["un", "deux"], "B": [0.5, 0.6]})
        store.add(name="zoo", metadata={'hh': 'kk'}, content=df)
        got = list(store.enumerate_content(name="zoo"))
        self.assertEqual(len(got), 1)
        record = got[0]
        name = record['name']
        self.assertEqual(name, "zoo")
        self.assertIn("date", record)
        content = record['content']
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqualDataFrame(df, content)
        meta = record['metadata']
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta, {'hh': 'kk'})
        got = list(store.enumerate(name="zoo"))
        self.assertEqual(len(got), 1)

        # data
        idfile = record['id']
        store.add_data(idfile=idfile, name="ZOO", value="5.6")
        res = list(store.enumerate_data(idfile))
        self.assertEqual(len(res), 1)
        del res[0]['date']
        self.assertEqual(res, [{'id': 1, 'idfile': 1, 'name': 'ZOO',
                                'value': 5.6}])

        # data join
        res = list(store.enumerate_data(idfile, join=True))
        self.assertEqual(len(res), 1)
        del res[0]['date']
        self.assertEqual(
            res, [{'id': 1, 'idfile': 1, 'name': 'ZOO',
                   'name_f': 'zoo', 'value': 5.6}])

    def test_file_store_exc(self):
        temp = get_temp_folder(__file__, "temp_file_storage_exc")
        name = os.path.join(temp, "filestore.db3")
        store = SqlLite3FileStore(name)
        df = pandas.DataFrame({"A": ["un", "deux"], "B": [0.5, 0.6]})
        self.assertRaise(
            lambda: store.add(name="zoo", metadata="{'hh': 'kk'}",
                              content=df),
            TypeError)

    def test_file_store1(self):
        temp = get_temp_folder(__file__, "temp_file_storage")
        name = os.path.join(temp, "filestore.db3")
        SqlLite3FileStore(name)
        SqlLite3FileStore(name)


if __name__ == "__main__":
    unittest.main()
