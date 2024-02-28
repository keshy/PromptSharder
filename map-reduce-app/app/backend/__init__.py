from pymongo import MongoClient


class mClient:
    def __init__(self, host='localhost', port=27017, username='root', password='example', database='ldp'):
        m = MongoClient(f'mongodb+src://{username}:{password}@{host}:{port}/{database}')
        self.m_client = m.get_database()

    def insert_job_meta(self, document, collection='ldb_jobs'):
        coll = self.m_client.create_collection(collection)
        result = coll.insert_one(document)
        if not result:
            raise Exception('Could not insert document to mongo. Db connectivity error')

    def look_up_job_meta(self, job_id, collection='ldb_jobs'):
        coll = self.m_client.create_collection(collection)
        document = coll.find_one(filter=job_id)
        if not document:
            return None
        else:
            return document

    def list_jobs(self, collection='ldb_jobs', limit=10):
        coll = self.m_client.create_collection(collection)
        list = coll.find().limit(limit)
        return list
