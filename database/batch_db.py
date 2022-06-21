import logging
import pymongo

from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI, DATABASE_NAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


@instance.register
class Batch_File(Document):
    unique_id = fields.StrField(attribute='_id')
    file_id = fields.StrField(allow_none=True)
    file_ref = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        collection_name = "UFS_Batch"


async def save_file(unique_id, file_id, file_ref, caption):
    """Save batch file in database"""
    try:
        file = Batch_File(
            unique_id=unique_id,
            file_id=file_id,
            file_ref=file_ref,
            caption=caption,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(caption + " is already saved in database")
            return False, 0
        else:
            logger.info(caption + " is saved in database")
            return True, 1


async def get_batch(unique_id):
    mycol = mydb["UFS_Batch"]
    query = unique_id.strip()

    query = mycol.find({'_id': query})

    try:
        for file in query:
            unique_id = file['_id']
            file_id = file['file_id']
            file_ref = file['file_ref']
            caption = file['caption']
            try:
                alert = file['alert']
            except:
                alert = None
        return unique_id, file_id, file_ref, caption
    except:
        return None, None, None, None
