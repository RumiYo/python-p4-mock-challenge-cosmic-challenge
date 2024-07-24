from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='planet')
    scientists = association_proxy('missions','scientist', creator=lambda project_obj:Mission(project=project_obj))

    # Add serialization rules
    serialize_rules = ('-missions.planet', '-scientists.planets', '-scientists.missions')

    def to_dict_2(self):
        return {
            'id': self.id,
            'name': self.name,
            'distance_from_earth': self.distance_from_earth,
            'nearest_star': self.nearest_star
        }


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='scientist')
    planets = association_proxy('missions', 'planet', creator=lambda project_obj:Mission(project=project_obj))

    # Add serialization rules
    serialize_rules = ('-missions.scientist', '-planets')

    # Add validation
    @validates('field_of_study')
    def validates_field_of_study(self, key, value):
        if not value:
            raise ValueError('Field of Study cannot be empty')
        return value

    @validates('name')
    def validates_name(self, key, name):
        if not name:
            raise ValueError('Name cannot be empty')
        return name
    

    def to_dict_2(self):
        return {
            'id': self.id,
            'name': self.name,
            'field_of_study': self.field_of_study
        }


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id =  db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    # Add serialization rules
    serialize_rules = ('-scientist.missions','-scientist.planets', '-planet.missions', '-planet.scientists')

    # Add validation
    @validates('name')
    def validates_name(self, key, value):
        if not value:
            raise ValueError('Name cannot be empty')
        return value

    @validates('scientist_id')
    def validates_scientistId(self, key, value):
        if not value:
            raise ValueError('Scientist cannot be empty')
        return value


# add any models you may need.
