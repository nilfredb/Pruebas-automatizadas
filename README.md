# 🧪 Selenium Automation Testing Project

This project demonstrates automated testing using **Selenium WebDriver** and **pytest**, including HTML report generation and screenshot capture on failures.

---

## 🚀 Features

* ✅ Automated browser testing with Selenium
* ✅ Test execution with pytest
* ✅ HTML reports generation
* ✅ Screenshot capture on failures
* ✅ Structured test organization
* ✅ Simple web app (Flask) for testing scenarios

---

## 📁 Project Structure

```
TAREA_4/
│
├── app.py                 # Flask application
├── database.db           # Local database (ignored in git)
├── requirements.txt      # Project dependencies
├── .gitignore
│
├── tests/
│   ├── test_selenium_pytest.py
│   ├── old_test_selenium.py
│
├── templates/            # HTML templates
├── static/               # CSS / JS files
│
├── reports/              # Generated test reports (ignored)
├── screenshots/          # Screenshots on failure (ignored)
│
├── venv/                 # Virtual environment (ignored)
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <https://github.com/nilfredb/Pruebas-automatizadas.git>
cd Pruebas-automatizadas
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

* Windows:

```bash
venv\Scripts\activate
```

* Linux / Mac:

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
python app.py
```

The app will be available at:

```
http://127.0.0.1:5000
```

---

## 🧪 Running Tests

Basic execution:

```bash
pytest
```

---

### 📊 Generate HTML Report

```bash
pytest tests/test_selenium_pytest.py --html=reports/report.html --self-contained-html
```

Then open:

```
reports/report.html
```

---

## 📸 Screenshots on Failure

When a test fails, a screenshot is automatically saved in:

```
screenshots/
```

---

## 🧠 Technologies Used

* Python 🐍
* Selenium WebDriver 🌐
* pytest 🧪
* Flask 🔥

---

## 💡 Future Improvements

* Add Page Object Model (POM)
* Parallel test execution
* CI/CD integration (GitHub Actions)
* Docker support

---

## 👨‍💻 Author

**Nilfred Báez**
Full Stack Developer | Automation Enthusiast

---

## 📄 License

This project is for educational purposes.
