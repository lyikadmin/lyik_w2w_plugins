import apluggy as pluggy
from pymongo import MongoClient

from lyikpluginmanager import getProjectName, IdGenSpec, ContextModel


impl = pluggy.HookimplMarker(getProjectName())


class IdGen(IdGenSpec):
    BASE_STRING = "BRANCH01"
    COLLECTION_NAME = "id_gen_sequence"

    def get_next_sequence(self, context: ContextModel):
        CONN_URL = context.config.get("DB_CONN_URL")
        DB_NAME = context.config.get("ORG_DB")
        client = MongoClient(CONN_URL)
        db = client[DB_NAME]

        result = db[self.COLLECTION_NAME].find_one_and_update(
            {"_id": "id_gen"},
            {"$inc": {"sequence": 1}},
            upsert=True,
            return_document=True,
        )
        gen_id = f"{self.BASE_STRING}{str(result['sequence']).zfill(5)}"
        return gen_id

    @impl
    async def idGen(self, context: ContextModel):
        return self.get_next_sequence(context=context)
