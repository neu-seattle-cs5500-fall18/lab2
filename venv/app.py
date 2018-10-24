from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, marshal, fields
from random import randint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, title='HangMan Game', version='2.0', description='8 Letter Hangman')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///postgres'
ns = api.namespace('Hangman', description='We are going to play hangman. '
                                          'Please only guess lowercase letters. You only have 6 guesses')
parser = api.parser()
hangman_database = SQLAlchemy(app)

class single_game(hangman_database.Model):
    id = hangman_database.Column(hangman_database.Integer, primary_key=True)
    magic_word = hangman_database.Column(hangman_database.String)
    known_letters = hangman_database.Column(hangman_database.String)
    tries_left = hangman_database.Column(hangman_database.Integer)
    guessed_letters = hangman_database.Column(hangman_database.String)


hangman_database.create_all()

@ns.route('/game')
@app.route('/game', methods=['GET', 'POST'])
class make_game(Resource):

    BagOfWords = ["zigzaggy", "skipjack", "aardvark", "butthead", "testings", "zabajone", "jezebels", "cybersex"]
    MagicWord = BagOfWords[randint(0, 7)]
    known = "********"
    tries = 6
    word_bank = ""

    @ns.doc("Creates a new game and returns the game ID")
    def post(self):
        i = 0
        while hangman_database.session.query(single_game.id).filter_by(id=i).scalar() is not None:
            i = i + 1
        game_to_be_added = single_game(id = i,
                                       magic_word = self.MagicWord,
                                       known_letters = self.known,
                                       tries_left = self.tries,
                                       guessed_letters = self.word_bank)
        hangman_database.session.add(game_to_be_added)
        hangman_database.session.commit()
        hangman_database.session.close()
        return "this is the game ID " + i



@ns.route('/guess')
@app.route('/guess', methods=['GET', 'POST'])
class play_game(Resource):
    BagOfWords = ["zigzaggy", "skipjack", "aardvark", "butthead", "testings", "zabajone", "jezebels", "cybersex"]
    MagicWord = BagOfWords[randint(0, 7)]
    known = "********"
    tries = 6
    word_bank = ""


    @ns.doc("Retrieves the current state of this game")
    def get(self):
        curr_state = {
            "message": "this is the current state of the game",
            "known": self.known,
            "tries": self.tries,
            "guessed": self.word_bank
        }
        return jsonify(curr_state)



    @ns.doc("Guess a single lower case letter")
    @ns.param('letter', 'the letter you are guessing')
    @app.route('/put/<string:letter>')
    def put(self):
        letter = request.args.get('letter')
        curr_state = {
            "message": "",
            "known": self.known,
            "tries": self.tries,
            "guessed": self.word_bank
        }



        if "*" not in self.known:
            return "YOU WIN"

        if (self.tries == 0):
            return "YOU LOSE"

        if (len(letter) != 1):
            curr_state["message"] = "you can only guess 1 letter at a time"
            return jsonify(curr_state)
        if letter in self.word_bank:
            curr_state["message"] = "You have already guessed that letter!"
            return jsonify(curr_state)
        if letter not in "abcdefghijklmnopqrstuvwxyz":
            curr_state["message"] = "Must be a lower case letter!"
            return jsonify(curr_state)

        if letter not in self.MagicWord:
            self.tries = self.tries - 1
            curr_state["tries"] = self.tries
            self.word_bank = self.word_bank + letter
            curr_state["message"] = "The letter " + letter + " is not it our word"
            return jsonify(curr_state)

        charArray = list(self.known)
        for i in range(0,len(self.MagicWord)):
            if letter == self.MagicWord[i]:
                charArray[i] = self.MagicWord[i]

        self.known = "".join(charArray)
        curr_state["message"] = "The letter " + letter + " is in our word!"
        curr_state["known"] = self.known
        curr_state["tries"] = self.tries
        curr_state["guessed"] = self.word_bank

        return jsonify(curr_state)



if __name__ == '__main__':
    app.run(debug=True)