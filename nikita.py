# pythonspot.com
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from sklearn.externals import joblib
import requests
import json
import pickle
import numpy as np
import pandas as pd

 
# musixmatch api base url
base_url = "https://api.musixmatch.com/ws/1.1/"

# your api key
api_key = "&apikey=5e6203280f5c220a14303055a070091d"

track_charts = "chart.tracks.get"
lyrics_url = "track.lyrics.get?track_id="

format_url = '?format=json&callback=callback&country='

vect = pickle.load(open('countv.p','rb'))
clf = pickle.load(open('clf_countv.p','rb'))
le = pickle.load(open('label_encoder.p','rb'))


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

class ReusableForm(Form):
    name = TextAreaField('Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required(), validators.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
 
 
def classify(text):
    x_vect = vect.transform([text])
    proba = np.max(clf.predict_proba(x_vect))
    pred = clf.predict(x_vect)[0]
    print(pred)
    label = le.inverse_transform([pred])
    return label

@app.route('/predict', methods=['GET','POST'])
def make_prediction():
    countryCode = request.form.get('country')
    form = ReusableForm(request.form)
    api_call = base_url + track_charts + format_url + countryCode + api_key
    print(api_call)
    req = requests.get(api_call)
    result = req.json()
    data = json.dumps(result, sort_keys=True, indent=2)
    d = json.loads(data)
    track_ids = [x['track']['track_id'] for x in d['message']['body']['track_list']]
    track_name = [x['track']['track_name'] for x in d['message']['body']['track_list']]
    artist_name = [x['track']['artist_name']for x in d['message']['body']['track_list']]
    print(track_name)
    print(artist_name)
    mood = ''
    text = ''

 data = pd.DataFrame(np.array([[track_id,track_name,artist_name,lyrics,mood,emoji]]),columns = ['Song Title','Artist Name','Lyrics','Mood','Emoji'])
 data.set_index(['track_name'], inplace=True)
    data.set_index(['artist_name'], inplace=True)    
    data.index.name=None
    return render_template('results.html',tables=[data.to_html(classes='data')],titles = ['Song Title','Artist Name','Lyrics', 'Mood', 'Emoji',],country=countryCode)

    
    
    
    for id in track_ids:
        api_cal = base_url + lyrics_url + str(id) + api_key
        
        r = requests.get(api_cal)
        dat = r.json()
        
        text = dat['message']['body']['lyrics']['lyrics_body'].split('...')[0]
        mood = classify(text)[0]
       
        break
        
   
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    return render_template('hello.html', form=form)
	
@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("test.html",result = result)
	
 
if __name__ == "__main__":
    # Getting the classifier ready
    app.run()
