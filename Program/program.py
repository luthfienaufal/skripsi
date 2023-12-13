from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/rekomendasi'  # Ganti sesuai dengan detail MySQL Anda
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Rekomendasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jurusan_rekomendasi = db.Column(db.String(50))

# Membaca dataset dari file Excel untuk jurusan IPA
dataframe_ipa = pd.read_excel(r'E:\KULIAH\SKRIPSWEET\program\data_nilai.xlsx', sheet_name='Sheet3')

# Membaca dataset dari file Excel untuk jurusan IPS
dataframe_ips = pd.read_excel(r'E:\KULIAH\SKRIPSWEET\program\data_nilai.xlsx', sheet_name='Sheet2')

X_train_ipa = dataframe_ipa[['Biologi', 'Fisika', 'Kimia', 'Matematika']]
y_train_ipa = dataframe_ipa['Jurusan']

X_train_ips = dataframe_ips[['Sosiologi', 'Ekonomi', 'Sejarah', 'Geografi', 'Matematika']]
y_train_ips = dataframe_ips['Jurusan']

clf_ipa = DecisionTreeClassifier(criterion='gini')  # Menggunakan Gini impurity
clf_ipa = clf_ipa.fit(X_train_ipa, y_train_ipa)

clf_ips = DecisionTreeClassifier(criterion='gini')  # Menggunakan Gini impurity
clf_ips = clf_ips.fit(X_train_ips, y_train_ips)

majors = ["Teknik Informatika", "Sistem Informasi", "Teknik Elektro", "Teknik Kimia", "Kimia", "Ilmu Hukum", "Hubungan Internasional", "Ilmu Pemerintahan", "Teknik Mesin", "Teknik Industri", "Teknik Metalurgi", "Manajemen", "Psikologi", "Farmasi", "Kedokteran", "Kedokteran Gigi"]

def gini_index(y):
    total_samples = len(y)
    class_counts = y.value_counts()
    impurity = 1 - sum((count/total_samples)**2 for count in class_counts)
    return impurity

def goodness_of_split(gini_t, gini_t_l, gini_t_r, samples_l, samples_r, total_samples):
    p_l = samples_l / total_samples
    p_r = samples_r / total_samples
    goodness = gini_t - p_l * gini_t_l - p_r * gini_t_r
    return goodness

# Rute untuk halaman menu
@app.route('/menu')
def menu():
    return render_template('menu.html')

# Rute untuk halaman utama
@app.route('/', methods=['GET', 'POST'])
def index():
    recommended_major = None  # Inisialisasi rekomendasi jurusan

    if request.method == 'POST':
        pilihan_jurusan = request.form['jurusan']

        if pilihan_jurusan == 'IPA':
            # Periksa apakah input adalah string yang valid dan bukan string kosong
            nilai_biologi = request.form['biologi']
            nilai_fisika = request.form['fisika']
            nilai_kimia = request.form['kimia']
            nilai_matematika = request.form['matematika']

            if nilai_biologi and nilai_fisika and nilai_kimia and nilai_matematika:
                nilai_biologi = int(nilai_biologi)
                nilai_fisika = int(nilai_fisika)
                nilai_kimia = int(nilai_kimia)
                nilai_matematika = int(nilai_matematika)
                
                data_to_predict = pd.DataFrame({'Biologi': [nilai_biologi], 'Fisika': [nilai_fisika], 'Kimia': [nilai_kimia], 'Matematika': [nilai_matematika]})
                predicted_major = clf_ipa.predict(data_to_predict)[0]
                recommended_major = majors[predicted_major]
        elif pilihan_jurusan == 'IPS':
            # Periksa apakah input adalah string yang valid dan bukan string kosong
            nilai_sosiologi = request.form['sosiologi']
            nilai_ekonomi = request.form['ekonomi']
            nilai_sejarah = request.form['sejarah']
            nilai_geografi = request.form['geografi']
            nilai_matematika_ips = request.form['matematika_ips']  # Ubah agar tidak ada konflik dengan nilai_matematika di IPA

            if nilai_sosiologi and nilai_ekonomi and nilai_sejarah and nilai_geografi and nilai_matematika_ips:
                nilai_sosiologi = int(nilai_sosiologi)
                nilai_ekonomi = int(nilai_ekonomi)
                nilai_sejarah = int(nilai_sejarah)
                nilai_geografi = int(nilai_geografi)
                nilai_matematika_ips = int(nilai_matematika_ips)

                data_to_predict = pd.DataFrame({'Sosiologi': [nilai_sosiologi], 'Ekonomi': [nilai_ekonomi], 'Sejarah': [nilai_sejarah], 'Geografi': [nilai_geografi], 'Matematika': [nilai_matematika_ips]})
                predicted_major = clf_ips.predict(data_to_predict)
                recommended_major = majors[predicted_major[0]]

        else:
            return "Pilihan Jurusan tidak valid"

        # Alihkan ke halaman result.html dan kirim hasil rekomendasi sebagai argumen
        return redirect(url_for('result', recommended_major=recommended_major))

    return render_template('index.html', recommended_major=recommended_major)

@app.route('/result', methods=['GET'])
def result():
    # Dapatkan hasil rekomendasi dari argumen URL
    recommended_major = request.args.get('recommended_major')
    if recommended_major:
        rekomendasi = Rekomendasi(jurusan_rekomendasi=recommended_major)
        db.session.add(rekomendasi)
        db.session.commit()

    # Tampilkan halaman result.html dan kirim hasil rekomendasi
    return render_template('result.html', recommended_major=recommended_major)

if __name__ == '__main__':
    # Ganti menjadi "/menu" agar ke menu.html saat membuka aplikasi
    app.run(debug=True, host='0.0.0.0', port=5000)
