import os
import time
import sqlite3
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:5000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "database.db")

# Control general de velocidad visual de las pruebas
UI_DELAY = 0.0


def clear_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()


def insert_task(title, description=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


class TaskManagerSeleniumTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        clear_tasks()
        self.driver.delete_all_cookies()
        self.driver.get(f"{BASE_URL}/login")
        self.pause()

    def pause(self, seconds=None):
        time.sleep(UI_DELAY if seconds is None else seconds)

    def login(self, email="admin@test.com", password="123456"):
        email_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        password_input = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(By.ID, "login-btn")

        email_input.clear()
        self.pause(0.4)
        email_input.send_keys(email)
        self.pause(0.5)

        password_input.clear()
        self.pause(0.4)
        password_input.send_keys(password)
        self.pause(0.5)

        login_button.click()
        self.pause(1)

    def go_to_create_task(self):
        create_link = self.wait.until(
            EC.element_to_be_clickable((By.ID, "create-task-link"))
        )
        create_link.click()
        self.pause(1)

    def create_task(self, title, description=""):
        self.go_to_create_task()

        title_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "task-title"))
        )
        desc_input = self.driver.find_element(By.ID, "task-desc")
        save_button = self.driver.find_element(By.ID, "save-task-btn")

        title_input.clear()
        self.pause(0.4)
        title_input.send_keys(title)
        self.pause(0.5)

        desc_input.clear()
        self.pause(0.4)
        desc_input.send_keys(description)
        self.pause(0.5)

        save_button.click()
        self.pause(1)

    def open_edit_task(self, task_id):
        edit_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, f"edit-task-{task_id}"))
        )
        edit_button.click()
        self.pause(1)

    def edit_task(self, task_id, new_title, new_description=""):
        self.open_edit_task(task_id)

        title_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "edit-task-title"))
        )
        desc_input = self.driver.find_element(By.ID, "edit-task-desc")
        update_button = self.driver.find_element(By.ID, "update-task-btn")

        title_input.clear()
        self.pause(0.4)
        title_input.send_keys(new_title)
        self.pause(0.5)

        desc_input.clear()
        self.pause(0.4)
        desc_input.send_keys(new_description)
        self.pause(0.5)

        update_button.click()
        self.pause(1)

    def delete_task(self, task_id):
        delete_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, f"delete-task-{task_id}"))
        )
        delete_button.click()
        self.pause(1)

    def get_body_text(self):
        return self.driver.page_source

    # =========================
    # HU-01 LOGIN
    # =========================

    def test_hu01_login_happy_path(self):
        self.login()

        self.wait.until(EC.url_contains("/dashboard"))
        body_text = self.get_body_text()

        self.assertIn("Task Dashboard", body_text)
        self.assertIn("Welcome, admin@test.com", body_text)

    def test_hu01_login_negative_wrong_password(self):
        self.login(password="wrongpass")

        body_text = self.get_body_text()
        self.assertIn("Credenciales inválidas.", body_text)

    def test_hu01_login_limit_empty_fields(self):
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "login-btn"))
        )
        login_button.click()
        self.pause(1)

        body_text = self.get_body_text()
        self.assertIn("Todos los campos son obligatorios.", body_text)

    # =========================
    # HU-02 CREATE TASK
    # =========================

    def test_hu02_create_task_happy_path(self):
        self.login()
        self.create_task("Comprar pan", "Ir a la tienda en la tarde")

        self.wait.until(EC.url_contains("/dashboard"))
        body_text = self.get_body_text()

        self.assertIn("Tarea creada correctamente.", body_text)
        self.assertIn("Comprar pan", body_text)

    def test_hu02_create_task_negative_empty_title(self):
        self.login()
        self.go_to_create_task()

        desc_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "task-desc"))
        )
        save_button = self.driver.find_element(By.ID, "save-task-btn")

        desc_input.send_keys("Descripción sin título")
        self.pause(0.5)
        save_button.click()
        self.pause(1)

        body_text = self.get_body_text()
        self.assertIn("El título es obligatorio.", body_text)

    def test_hu02_create_task_limit_max_length(self):
        self.login()
        max_title = "A" * 100
        self.create_task(max_title, "")

        self.wait.until(EC.url_contains("/dashboard"))
        body_text = self.get_body_text()

        self.assertIn("Tarea creada correctamente.", body_text)
        self.assertIn(max_title, body_text)

    # =========================
    # HU-03 VIEW TASK LIST
    # =========================

    def test_hu03_view_task_list_happy_path(self):
        insert_task("Tarea 1", "Descripción 1")
        insert_task("Tarea 2", "Descripción 2")

        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        body_text = self.get_body_text()
        self.assertIn("Tarea 1", body_text)
        self.assertIn("Tarea 2", body_text)

    def test_hu03_view_task_list_negative_without_login(self):
        self.driver.get(f"{BASE_URL}/dashboard")
        self.pause(1)

        self.wait.until(EC.url_contains("/login"))
        body_text = self.get_body_text()

        self.assertIn("Login", body_text)

    def test_hu03_view_task_list_limit_empty_list(self):
        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        body_text = self.get_body_text()
        self.assertIn("No tasks available.", body_text)

    # =========================
    # HU-04 EDIT TASK
    # =========================

    def test_hu04_edit_task_happy_path(self):
        task_id = insert_task("Tarea vieja", "Descripción vieja")

        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        self.edit_task(task_id, "Tarea actualizada", "Nueva descripción")

        self.wait.until(EC.url_contains("/dashboard"))
        body_text = self.get_body_text()

        self.assertIn("Tarea actualizada correctamente.", body_text)
        self.assertIn("Tarea actualizada", body_text)
        self.assertNotIn("Tarea vieja", body_text)

    def test_hu04_edit_task_negative_empty_title(self):
        task_id = insert_task("Tarea editable", "Descripción")

        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        self.open_edit_task(task_id)

        title_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "edit-task-title"))
        )
        update_button = self.driver.find_element(By.ID, "update-task-btn")

        title_input.clear()
        self.pause(0.5)
        update_button.click()
        self.pause(1)

        body_text = self.get_body_text()
        self.assertIn("El título es obligatorio.", body_text)

    def test_hu04_edit_task_limit_max_length(self):
        task_id = insert_task("Base", "Descripción base")

        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        max_title = "B" * 100
        self.edit_task(task_id, max_title, "Descripción límite")

        self.wait.until(EC.url_contains("/dashboard"))
        body_text = self.get_body_text()

        self.assertIn("Tarea actualizada correctamente.", body_text)
        self.assertIn(max_title, body_text)

    # =========================
    # HU-05 DELETE TASK
    # =========================

    def test_hu05_delete_task_happy_path(self):
        task_id = insert_task("Tarea a eliminar", "Eliminar esta tarea")

        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        self.delete_task(task_id)

        body_text = self.get_body_text()
        self.assertIn("Tarea eliminada correctamente.", body_text)
        self.assertNotIn("Tarea a eliminar", body_text)

    def test_hu05_delete_task_negative_nonexistent_task(self):
        self.login()
        self.driver.get(f"{BASE_URL}/tasks/delete/9999")
        self.pause(1)

        # Como la ruta es POST, una visita GET normalmente no elimina.
        # Lo que realmente nos importa aquí es que la app no colapse.
        body_text = self.get_body_text()
        self.assertTrue("405" in body_text or "Method Not Allowed" in body_text)

    def test_hu05_delete_task_limit_delete_only_task(self):
        task_id = insert_task("Única tarea", "Solo existe una")

        self.login()
        self.wait.until(EC.url_contains("/dashboard"))
        self.pause(1)

        self.delete_task(task_id)

        body_text = self.get_body_text()
        self.assertIn("Tarea eliminada correctamente.", body_text)
        self.assertIn("No tasks available.", body_text)

    # =========================
    # HU-06 LOGOUT
    # =========================

    def test_hu06_logout_happy_path(self):
        self.login()

        logout_link = self.wait.until(
            EC.element_to_be_clickable((By.ID, "logout-link"))
        )
        logout_link.click()
        self.pause(1)

        self.wait.until(EC.url_contains("/login"))
        body_text = self.get_body_text()

        self.assertIn("Sesión cerrada correctamente.", body_text)
        self.assertIn("Login", body_text)

    def test_hu06_logout_negative_access_protected_after_logout(self):
        self.login()

        logout_link = self.wait.until(
            EC.element_to_be_clickable((By.ID, "logout-link"))
        )
        logout_link.click()
        self.pause(1)

        self.driver.get(f"{BASE_URL}/dashboard")
        self.pause(1)

        self.wait.until(EC.url_contains("/login"))
        body_text = self.get_body_text()
        self.assertIn("Login", body_text)

    def test_hu06_logout_limit_without_authentication(self):
        self.driver.get(f"{BASE_URL}/logout")
        self.pause(1)

        # Como logout requiere login, debe redirigir o mantener una respuesta controlada.
        body_text = self.get_body_text()
        self.assertIn("Login", body_text)


if __name__ == "__main__":
    unittest.main()