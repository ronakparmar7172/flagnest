import flask
import psycopg2
from config import config
from flask import send_file, jsonify
from PIL import Image
import io
import os
app = flask.Flask(__name__)



def connect_to_postgres():

    try:
        # Establish the connection
        connection = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=config.DB_PORT,  # Default PostgreSQL port
            sslmode=config.DB_SSLMODE
        )

        return connection
        

    except Exception as error:
        return jsonify({"message": f"Error connecting to database: {error}"}), 500




@app.route("/" , methods=["GET"])
def home():
    try : 
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        return jsonify({"message": f"Connected to PostgreSQL database. Version: {db_version[0]}"}), 200

    except Exception as error:
        return jsonify({"message": f"Error connecting to database: {error}"}), 500


from flask import send_file, jsonify
from PIL import Image
import io
import os

@app.route("/flags/<name>/<int:size>", methods=["GET"])
def get_flag(name, size):
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT public.get_country_flag(%s);",
            (name,)
        )

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result or not result[0]:
            return jsonify({"message": "Flag not found"}), 404

        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(PROJECT_ROOT, result[0])

        if not os.path.isfile(image_path):
            return jsonify({
                "message": "Image file not found",
                "path": image_path
            }), 404

        # Open and resize image
        img = Image.open(image_path)
        img = img.resize((size, size), Image.LANCZOS)

        # Save to memory
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=8000)