from peewee import *
import datetime

# create a peewee database instance -- our models will use this database to
# persist information
DATABASE = "data/sqlite/BridleCrew"
database = SqliteDatabase(DATABASE)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns) declaratively, like django
class Athlete(BaseModel):
    name = CharField()

# this model contains two foreign keys to user -- it essentially allows us to
# model a "many-to-many" relationship between users.  by querying and joining
# on different columns we can expose who a user is "related to" and who is
# "related to" a given user
class Run(BaseModel):
    athlete_id = ForeignKeyField(Athlete)
    date = IntegerField()
    distance = IntegerField()
    time = IntegerField()

    class Meta:
        # `indexes` is a tuple of 2-tuples, where the 2-tuples are
        # a tuple of column names to index and a boolean indicating
        # whether the index is unique or not.
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            ('athlete_id', True)
        )


def get_athlete_id(athlete):
    i, _ = Athlete.get_or_create(name=athlete)
    return i.id


def add_run_from_athlete(athlete, date, distance, time):
    i = get_athlete_id(athlete)
    Run.create(
        athlete_id=i,
        date=date,
        distance=distance,
        time=time)

