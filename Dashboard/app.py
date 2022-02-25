from flask import Flask, request, jsonify, render_template, url_for
from flask import g
import pickle
import dill
import pandas as pd
from collections import OrderedDict
import math

app = Flask(__name__)

model = pickle.load(open('data/best_pipes.pkl', 'rb'))
model_lime = pickle.load(open('data/model_lime.pkl', 'rb'))

df_results = pd.read_csv("data/Results.csv")

pipeline_lime = pickle.load(open('data/pipeline_lime.pkl', 'rb'))
X_test = pickle.load(open('data/X_test.pkl', 'rb'))
y_test = pickle.load(open('data/y_test.pkl', 'rb'))
y_pred = model.predict(X_test)

features_lime = pickle.load(open('data/features_lime.pkl', 'rb'))

X_test_lime = pipeline_lime.transform(X_test)

with open('data/explainer', 'rb') as f:
    explainer = dill.load(f)


@app.route('/')
def home():
    clients = X_test['SK_ID_CURR'].sort_values(ascending=False).to_list()
    return render_template('index.html', clients=clients,
                                        logo=url_for('static', filename='img/Logo.jpg'))


@app.route('/dashboard/', methods=['POST'])
def dashboard():
    global numero_client, age, genre, index_df

    numero_client = request.form.get("Numéro de dossier")
    numero_client = int(numero_client)

    index_df = X_test[X_test['SK_ID_CURR'] == numero_client].index[0]

    age = int(X_test.loc[index_df, 'DAYS_BIRTH']/(-365))
    code_genre = X_test.loc[index_df, 'CODE_GENDER']

    df_results.loc[0,"client"] = numero_client
    df_results.loc[0, "index_df"] = index_df

    print('Dashboard')
    print(index_df)

    if code_genre == 0:
        genre = "Homme"
    else:
        genre = "Femme"

    return render_template('dashboard.html',
                           client_number=numero_client,
                           age='{} ans'.format(age),
                           genre=genre)


@app.route('/results/', methods=['POST'])
def predict():
    global score

    index_df = df_results.loc[0, "index_df"]
    age = int(X_test.loc[index_df, 'DAYS_BIRTH'] / (-365))
    numero_client = df_results.loc[0, "client"]
    genre = df_results.loc[0, "genre"]
    print(index_df)
    prediction = model.predict_proba(X_test)[index_df][0]

    #prediction = model.predict_proba(X_test)[index_df][0]

    if prediction >= 0.55:
        score = "Accordé"
    elif prediction < 0.55 and prediction >= 0.45:
        score = "Défavorable - Dossier à revalider"
    else:
        score = "Refusé"

    return render_template('dashboard.html',
                           OK_pred='OK',
                           client_number=numero_client,
                           age='{} ans'.format(age),
                           genre=genre,
                           prediction_text='Prêt : {}'.format(score),
                           pred=round(prediction * 100, 2))


def lime_data():
    index_df = df_results.loc[0, "index_df"]
    numero_client = df_results.loc[0, "client"]
    genre = numero_client = df_results.loc[0, "genre"]
    explanation = explainer.explain_instance(X_test_lime[index_df], model_lime.predict_proba, num_features=20)
    liste_features_LIME = explanation.as_map()[1]
    features_explained_LIME = []

    for i in range(len(liste_features_LIME)):
        features_explained_LIME.append(features_lime[liste_features_LIME[i][0]])

    liste_radar_specifique = features_explained_LIME[:5]
    X_test_lime_df = pd.DataFrame(data=X_test_lime, columns=features_lime)
    return X_test_lime_df, liste_radar_specifique


@app.route('/LIME/', methods=['POST'])
def lime_plot():
    explanation = explainer.explain_instance(X_test_lime[index_df], model_lime.predict_proba, num_features=20)
    html_data = explanation.as_html()

    return render_template('dashboard.html', exp=html_data,
                           client_number=numero_client,
                           age='{} ans'.format(age),
                           genre=genre)


@app.route('/API/radar/')
def def_radar():
    global data_radar
    data_radar, liste_radar_specifique = lime_data()

    liste_radar_general = ['EXT_SOURCE_2', 'EXT_SOURCE_3', 'EXT_SOURCE_1', 'AMT_ANNUITY', 'PAYMENT_RATE']

    liste_radar = liste_radar_specifique + liste_radar_general
    liste_radar = list(OrderedDict.fromkeys(liste_radar))
    data_radar['TARGET'] = y_pred

    data_radar.loc[index_df, "TARGET"] = 3

    target_radar = data_radar.groupby('TARGET').median()
    target_radar = target_radar.reset_index()

    # New scale should be from 0 to 100.
    new_max = 100
    new_min = 0
    new_range = new_max - new_min

    # Do a linear transformation on each variable to change value to [0, 100].
    for factor in liste_radar:
        max_val = data_radar[factor].max()
        min_val = data_radar[factor].min()
        val_range = max_val - min_val
        target_radar[factor] = target_radar[factor].apply(
            lambda x: (((x - min_val) * new_range) / val_range) + new_min)

    titre_specifique = "Comparaison des profils clients - Sélection spécifique client"
    titre_general = "Comparaison des profils clients - Sélection générale"

    data_radar_specifique_inter = {}
    data_radar_general_inter = {}

    value_radar_specifique = target_radar.loc[:, liste_radar_specifique].values.tolist()
    value_radar_general = target_radar.loc[:, liste_radar_general].values.tolist()

    for ind in range(len(target_radar)):
        data_radar_specifique_inter[ind] = value_radar_specifique[ind]
        data_radar_general_inter[ind] = value_radar_general[ind]

    return jsonify({
        'status': 'ok',
        'data_1': data_radar_specifique_inter,
        'name_1': liste_radar_specifique,
        'titre_1': titre_specifique,
        'data_2': data_radar_general_inter,
        'name_2': liste_radar_general,
        'titre_2': titre_general,
            })


@app.route('/RADAR/', methods=['POST'])
def plot_radar():
    return render_template('dashboard.html',
                           OK_radar='OK',
                           client_number=numero_client,
                           age='{} ans'.format(age),
                           genre=genre)


@app.route('/HISTO/', methods=['POST'])
def histo_plot():
    index_df = df_results.loc[0, "index_df"]
    numero_client = df_results.loc[0, "client"]
    genre = numero_client = df_results.loc[0, "genre"]
    age = int(X_test.loc[index_df, 'DAYS_BIRTH'] / (-365))
    val = request.form.get("data_value")
    titre = ""
    unite = ""

    if val == "DAYS_BIRTH":
        titre = "Age"
        unite = " ans"
    elif val == "EXT_SOURCE_1":
        titre = "Score 1"
        unite = ""
    elif val == "EXT_SOURCE_2":
        titre = "Score 2"
        unite = ""
    elif val == "EXT_SOURCE_3":
        titre = "Score 3"
        unite = ""
    elif val == "DAYS_EMPLOYED":
        titre = "Ancienneté emploi"
        unite = " ans"
    elif val == "AMT_INCOME_TOTAL":
        titre = "Revenu annuel"
        unite = " $"
    elif val == "DAYS_ID_PUBLISH":
        titre = "Renouvellement carte d'identité"
        unite = " ans"
    elif val == "DAYS_LAST_PHONE_CHANGE":
        titre = "Renouvellement du téléphone"
        unite = " ans"
    elif val == "AMT_GOODS_PRICE":
        titre = "Montant de l'achat envisagé"
        unite = " $"

    data_histo = X_test.copy()
    data_histo['TARGET'] = y_pred
    data_histo['AMT_INCOME_TOTAL'] = data_histo['AMT_ANNUITY']/data_histo['ANNUITY_INCOME_PERC']
    data_histo['DAYS_BIRTH'] = data_histo['DAYS_BIRTH']/(-365)
    data_histo['DAYS_EMPLOYED'] = data_histo['DAYS_EMPLOYED'] / (-365)
    data_histo['DAYS_ID_PUBLISH'] = data_histo['DAYS_ID_PUBLISH'] / (-365)
    data_histo['DAYS_LAST_PHONE_CHANGE'] = data_histo['DAYS_LAST_PHONE_CHANGE'] / (-365)

    data_histo_yes = data_histo[data_histo['TARGET'] == 0][val].to_list()
    data_histo_no = data_histo[data_histo['TARGET'] == 1][val].to_list()
    data_histo_client = data_histo.loc[index_df, val]

    if math.isnan(data_histo_client):
        data_histo_client = 0
        titre = titre + "- Valeur client non définie"

    data_histo_yes = [x for x in data_histo_yes if math.isnan(x) == False]
    data_histo_no = [x for x in data_histo_no if math.isnan(x) == False]

    data_histo_client = int(data_histo_client)

    info_client = str(data_histo_client) + unite

    return render_template('dashboard.html',
                           OK_pred='NOK',
                           OK_histo='OK',
                           client_number=numero_client,
                           age='{} ans'.format(age),
                           genre=genre,
                           data_histo_titre=titre,
                           data_histo_yes=data_histo_yes,
                           data_histo_no=data_histo_no,
                           data_histo_client=data_histo_client,
                           info_client=info_client)


if __name__ == "__main__":
    app.run(debug=True)