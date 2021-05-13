# -*- coding: utf-8 -*-
#    Copyright (C) 2021  The Project TONA Authors
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
import peewee
from models.base import BaseModel
from models.habit import Habit

class HabitCheckin(BaseModel):
    
    class Meta:
        table_name = 'habit_checkin'

    habit_id = peewee.ForeignKeyField(Habit)
    name = peewee.TextField()
    checkin = peewee.DateField()


    @classmethod
    def prepare_fields(self, data, only=[], exclude=[], allowed={}):
        allowed = {
            'name': 'str',
            'checkin': 'date',
            'habit_id': 'int'
        }
        return super(HabitCheckin, self).prepare_fields(data, only=only, exclude=exclude, allowed=allowed)

def create_habit_checkin(**kwargs):
    data = HabitCheckin.prepare_fields(kwargs, only=['name', 'checkin','habit_id'])
    row = HabitCheckin.create(**data)
    return row.to_dict()