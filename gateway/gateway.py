from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return Gateway.run()


class Gateway:

    @staticmethod
    def run():
        print("Hello World...")
        return 'Return content'
