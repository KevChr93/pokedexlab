from sqlalchemy import Column, String, Integer
from models.entity import Entity
from sqlalchemy.event import listen

from app import db


class Pokemon(Entity, db.Model):
    __tablename__='pokemon'
    name=Column(String(100))
    hp=Column(String(4))
    type_1=Column(String(20))
    type_2=Column(String(20))
    attack=Column(Integer)
    defense=Column(Integer)
    special_attack=Column(Integer)
    special_defense=Column(Integer)
    total=Column(Integer)
    speed=Column(Integer)

    def __init__(self):
        super().__init__()
        Entity.__init__(self)

    def fromJSON(self, json_rec):
        if 'name' in json_rec:
            self.name = json_rec['name']
        else:
            raise Exception('The name field is required')

        self.hp = json_rec['hp'] if 'hp' in json_rec else ''
        self.type_1 = json_rec['type_1'] if 'type_1' in json_rec else ''
        self.type_2 = json_rec['type_2'] if 'type_2' in json_rec else ''
        self.attack = json_rec['attack'] if 'attack' in json_rec else 0
        self.defense = json_rec['defense'] if 'defense' in json_rec else 0
        self.special_attack = json_rec['sp_atk'] if 'sp_atk' in json_rec else 0
        self.special_defense= json_rec['sp_def'] if 'sp_def' in json_rec else 0
        self.total = json_rec['total'] if 'total' in json_rec else 0
        self.speed = json_rec['speed'] if 'speed' in json_rec else 0

    def toDict(self):
        repre = Entity.toDict(self)
        repre.update({
            'name': self.name,
            'hp':self.hp,
            'type_1':self.type_1,
            'type_2':self.type_2,
            'attack':self.attack,
            'defense':self.defense,
            'special_attack':self.special_attack,
            'special_defense':self.special_defense,
            'total':self.total,
            'speed':self.speed
        })
        return repre


def load_pkfile_into_table(target, connection, **kw):
    import json

    with open('pokedata.json') as fp:
        full_data = fp.read()
        fp.close()
        json_data = json.loads(full_data)
    print("Found {0} records".format(len(json_data)))
    for rec in json_data:
        rec_details = rec['fields']
        p = Pokemon()
        p.fromJSON(rec_details)
        db.session.add(p)
    db.session.commit()


listen(Pokemon.__table__, 'after_create', load_pkfile_into_table)