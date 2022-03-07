from flask import Flask, jsonify
import pickle

app = Flask(__name__)

# Lecture des diférentes données nécessaires au fonctionnement du dashboard
# pipeline du modèle de ML utilisé
model = pickle.load(open('data/best_pipes.pkl', 'rb'))

# Dataframe des données clients
X_test = pickle.load(open('data/X_test.pkl', 'rb'))


@app.route('/API/score/<numero_client>')
def API_pred(numero_client):
    # API qui retourne le score d'un client donné
    numero_client = int(numero_client)

    index_df = X_test[X_test['SK_ID_CURR'] == numero_client].index[0]

    prediction = model.predict_proba(X_test)[index_df][0]

    if prediction >= 0.55:
        score = "Accordé"
    elif prediction < 0.55 and prediction >= 0.45:
        score = "Défavorable - Dossier à revalider"
    else:
        score = "Refusé"

    pred = round(prediction * 100, 2)

    return jsonify({
        'prediction': pred,
        'score': score
    })


if __name__ == "__main__":
    app.run(debug=True)