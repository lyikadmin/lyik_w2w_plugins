import apluggy as pluggy
from pymongo import MongoClient

from lyikpluginmanager import getProjectName, IdGenSpec, ContextModel, PluginException
from lyikpluginmanager.annotation import RequiredVars
from typing import Annotated
from typing_extensions import Doc

impl = pluggy.HookimplMarker(getProjectName())


class IdGen(IdGenSpec):
    BASE_STRING = "BRANCH01"
    COLLECTION_NAME = "id_gen_sequence"

    def get_next_sequence(
        self,
        context: ContextModel,
        db_name: Annotated[str, Doc("Name of the db in the database")],
    ) -> Annotated[
        str, Doc("A unique generated id based on a sequence will be returned")
    ]:
        CONN_URL = context.config.get("DB_CONN_URL")
        if not CONN_URL:
            raise PluginException(f"Config doesn't have DB connection URL")
        DB_NAME = db_name
        client = MongoClient(CONN_URL)
        db = client[DB_NAME]
        if not db:
            raise PluginException(f"DB not found")

        try:
            result = db[self.COLLECTION_NAME].find_one_and_update(
                {"_id": "id_gen"},
                {"$inc": {"sequence": 1}},
                upsert=True,
                return_document=True,
            )
            gen_id = f"{self.BASE_STRING}{str(result['sequence']).zfill(5)}"
            return gen_id
        except Exception as e:
            raise PluginException(f"Failed to generate ID") from e

    @impl
    async def idGen(
        self,
        context: ContextModel,
        db_name: Annotated[str, Doc("Name of the db in the database")],
    ) -> Annotated[
        str, Doc("A unique generated id based on a sequence will be returned")
    ]:
        return self.get_next_sequence(context=context, db_name=db_name)
