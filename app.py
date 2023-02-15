from flask import current_app
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from Crypto.Cipher import AES
import hashlib

app = Flask(__name__)
app.secret_key = "ccencryption"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///credit_cards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

key = hashlib.sha256(b'my_secret_key').digest()

class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encrypted_number = db.Column(db.String(256))

    def __repr__(self):
        return f'<CreditCard {self.id}>'

# Define the padding value
padding = b'{'

# Define the function to pad the data
def pad(data):
    length = 16 - (len(data) % 16)
    data += bytes([length]) * length
    return data

# Define the function to unpad the data
def unpad(data):
    return data[:-data[-1]]

def encrypt(data):
    cipher = AES.new(key, AES.MODE_CBC, b'0000000000000000')
    padded_data = pad(data)
    ciphertext = cipher.encrypt(padded_data)
    return ciphertext

# Define the function to decrypt the data
def decrypt(ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, b'0000000000000000')
    padded_data = cipher.decrypt(ciphertext)
    data = unpad(padded_data)
    return data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/aes_cc", methods=['POST'])
def aes_cc():
    if request.method == 'POST':
        # Get the credit card number from the form
        card_number = request.form['ccnumber']

        with current_app.app_context():
            # Encrypt the credit card number
            encrypted_number = encrypt(card_number.encode('utf-8'))

            # Store the encrypted credit card number in the database
            credit_card = CreditCard(encrypted_number=encrypted_number)
            db.session.add(credit_card)
            db.session.commit()

            # Retrieve all credit cards from the database
            credit_cards = CreditCard.query.all()
            for cc in credit_cards:
                print("Encrypted Cards : ",cc.encrypted_number)
            # Decrypt each credit card number and add it to a list
            decrypted_cards = []
            for card in credit_cards:
                decrypted_number = decrypt(card.encrypted_number).decode('utf-8')
                decrypted_cards.append(decrypted_number)
        # Render the template with the decrypted credit card numbers
        flash("Encrypted Successfully!!")
        return render_template('index.html', credit_cards=decrypted_cards)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

