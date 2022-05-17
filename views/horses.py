import flask_praetorian
from flask import request
from flask_restx import abort, Resource, Namespace
from model import Horse, db, Runs_Horses
from schema import HorseSchema

api_horse = Namespace("Horses", "Horses management")

""" 
Client endopoints 
"""


@api_horse.route("/detail/<horse_id>")
class HorseController(Resource):
    @flask_praetorian.auth_required
    def get(self, horse_id):
        horse = Horse.query.get_or_404(horse_id)
        horseData = HorseSchema().dump(horse)

        timesFirst = Runs_Horses.query.filter(Runs_Horses.horse_id == horse_id, Runs_Horses.final_position == 1).count()
        timesSecond = Runs_Horses.query.filter(Runs_Horses.horse_id == horse_id,
                                               Runs_Horses.final_position == 2).count()
        timesThird = Runs_Horses.query.filter(Runs_Horses.horse_id == horse_id, Runs_Horses.final_position == 3).count()

        horseData['timesFirst'] = timesFirst
        horseData['timesSecond'] = timesSecond
        horseData['timesThird'] = timesThird

        return horseData


""" 
Admin endopoints 
"""


@api_horse.route("/<horse_id>")
class HorseController(Resource):
    @flask_praetorian.auth_required
    def get(self, horse_id):
        horse = Horse.query.get_or_404(horse_id)
        return HorseSchema().dump(horse)

    @flask_praetorian.roles_required("admin")
    def delete(self, horse_id):
        horse = Horse.query.get_or_404(horse_id)
        db.session.delete(horse)
        db.session.commit()
        return f"Deleted horse {horse_id}", 204

    @flask_praetorian.roles_required("admin")
    def put(self, horse_id):
        new_horse = HorseSchema().load(request.json)
        if str(new_horse.id) != horse_id:
            abort(400, "id mismatch")
        db.session.commit()
        return HorseSchema().dump(new_horse)


@api_horse.route("/")
class HorseListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return HorseSchema(many=True).dump(Horse.query.all())

    @flask_praetorian.roles_required("admin")
    def post(self):
        horse = HorseSchema().load(request.json)
        db.session.add(horse)
        db.session.commit()
        return HorseSchema().dump(horse), 201
