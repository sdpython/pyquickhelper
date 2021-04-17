"""
@brief      test log(time=4s)

"""
import unittest
import os
import pandas
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.server.filestore_fastapi import (
    create_fast_api_app, fast_api_submit, fast_api_query,
    fast_api_content, _get_password, _post_request)
from fastapi.testclient import TestClient  # pylint: disable=E0401
from pyquickhelper.server.filestore_sqlite import SqlLite3FileStore


class TestfileStoreRest(ExtTestCase):

    def test_simple_function1(self):
        self.assertRaise(
            lambda: _get_password(None, "IMPOSSIBLE"), RuntimeError)

    def test_simple_function2(self):
        from requests.exceptions import ConnectionError
        self.assertRaise(
            lambda: _post_request(None, None, None, None), AttributeError)
        self.assertRaise(
            lambda: _post_request(None, "http://localhost:7777", {}, "submit",
                                  timeout=1.),
            ConnectionError)

    def test_file_store(self):
        temp = get_temp_folder(__file__, "temp_file_storage_rest")
        name = os.path.join(temp, "filestore.db3")
        app = create_fast_api_app(name, "BBB")
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {'pyquickhelper': 'FastAPI to load and query files'})
        response = client.post(
            "/submit/", json=dict(name="essai", content="a,b\ne,0\nhh, 1.5",
                                  password="CCC"))
        self.assertEqual(response.status_code, 401)

        response = client.post(
            "/submit/", json=dict(name="essai", content="a,b\ne,0\nhh, 1.5",
                                  project="proj", password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertIn('date', js)
        self.assertNotIn('content', js)

        response = client.post(
            "/query/", json=dict(name="essai", password="CCC"))
        self.assertEqual(response.status_code, 401)

        response = client.post(
            "/query/", json=dict(name="essai", password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 1)

        response = client.post(
            "/query/", json=dict(password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 1)

        response = client.post(
            "/content/", json=dict(password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 1)

        response = client.post(
            "/metrics/", json=dict(name="essai", password="CCC"))
        self.assertEqual(response.status_code, 401)

        response = client.post(
            "/metrics/", json=dict(name="essai", password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 0)

        db = SqlLite3FileStore(name)
        db.submit_data(1, "essai", 0.67, comment="ok")

        response = client.post(
            "/metrics/", json=dict(name="essai", password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 1)
        self.assertEqual(js[0]['value'], 0.67)

        response = client.post(
            "/metrics/", json=dict(project="proj", password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 1)
        self.assertEqual(js[0]['value'], 0.67)

        response = client.post(
            "/metrics/", json=dict(password="BBB"))
        self.assertEqual(response.status_code, 200)
        js = response.json()
        self.assertEqual(len(js), 1)
        self.assertEqual(js[0]['value'], 0.67)

    def test_file_store_df(self):
        temp = get_temp_folder(__file__, "temp_file_storage_rest_df")
        name = os.path.join(temp, "filestore.db3")
        app = create_fast_api_app(name, "BBB")
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

        df = pandas.DataFrame(
            dict(A=[0, 5, 6], B=[4.5, 1, 1], C=["E", "R", "T"]))
        resp = fast_api_submit(df, client, team="AA", name="BB", project="CCC",
                               version=1, password="BBB")
        self.assertEqual(resp.status_code, 200)

        df = pandas.DataFrame(
            dict(A=[0, 5, 6], B=[4.5, 2, 2], C=["E", "R", "Z"]))
        resp = fast_api_submit(df, client, team="AA", name="BB", project="CCC",
                               version=2, password="BBB")
        self.assertEqual(resp.status_code, 200)

        res = fast_api_query(client, team="AA", name="BB", project="CCC",
                             password="BBB")
        exp = [{'id': 1, 'name': 'BB', 'format': '',
                'metadata': {'client': ['testclient', 50000]}, 'team': 'AA',
                'project': 'CCC', 'version': 1, 'format': 'df'},
               {'id': 2, 'name': 'BB', 'format': '',
                'metadata': {'client': ['testclient', 50000]}, 'team': 'AA',
                'project': 'CCC', 'version': 2, 'format': 'df'}]
        for r in res:
            del r['date']
        self.assertEqual(res, exp)

        df = fast_api_query(client, team="AA", name="BB", project="CCC",
                            password="BBB", as_df=True)
        cols = ['team', 'project', 'name', 'version']
        df = df[cols]
        mv = df.groupby(cols[:-1]).max()
        self.assertEqual(mv.shape, (1, 1))
        self.assertEqual(mv.iloc[0, 0], 2)

        content = fast_api_content(
            client, team="AA", name="BB", project="CCC",
            password="BBB", as_df=True)
        for c in content:
            self.assertIsInstance(c['content'], pandas.DataFrame)
            self.assertEqual(c['content'].shape, (3, 3))


if __name__ == "__main__":
    unittest.main()
