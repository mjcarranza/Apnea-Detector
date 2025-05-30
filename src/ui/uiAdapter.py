import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import time
import os

DB_PATH = "data/patientData/patient_data.json"
ICON_PATH = "assets/user_profile_icon.png"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def load_patient_data():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as file:
        try:
            data = json.load(file)
            return data.get("patient", {})
        except json.JSONDecodeError:
            return {}

def is_profile_complete():
    required_fields = ["age", "sex", "weight_(kg)", "height_(cm)", "bmi", "neck_circumference_(cm)"]
    data = load_patient_data()
    return all(data.get(field) and str(data.get(field)).strip() for field in required_fields)

def save_patient_data(data):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as file:
        json.dump({"patient": data}, file, indent=4)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sleep Apnea Detection System")
        self.geometry("800x600")
        self.minsize(600, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartScreen, ProfileForm, RecordingScreen):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartScreen if is_profile_complete() else ProfileForm)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

class StartScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Configurar el layout general
        self.grid_rowconfigure((0, 2), weight=1)  # Espacio arriba y abajo del botón
        self.grid_rowconfigure(1, weight=0)       # Fila del botón
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Welcome to the Sleep Apnea Detection System", font=("Arial", 20))
        title.grid(row=0, column=0, pady=20, sticky="n")

        # Botón Record (centrado, redondo)
        self.record_button = ctk.CTkButton(
            self,
            text="Record",
            text_color="white",
            fg_color="green",
            hover_color="#009900",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=150,
            corner_radius=75,  # Mitad del tamaño para que sea redondo
            command=self.start_recording
        )
        self.record_button.grid(row=1, column=0, pady=20)

        # Frame para botones en línea (abajo)
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)

        ctk.CTkButton(button_frame, text="Start Recording Session", width=200).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="View Session History", width=200).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Access User Profile", width=200, command=lambda: parent.show_frame(ProfileForm)).grid(row=0, column=2, padx=10)

    def start_recording(self):
        self.master.show_frame(RecordingScreen)



class RecordingScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recording = False
        self.start_time = None
        self.timer_thread = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Cronómetro
        self.timer_label = ctk.CTkLabel(self, text="00:00:00", font=ctk.CTkFont(size=40, weight="bold"))
        self.timer_label.grid(row=0, column=0, pady=30)

        # Botón Stop
        self.stop_button = ctk.CTkButton(
            self,
            text="Stop",
            text_color="white",
            fg_color="red",
            hover_color="#990000",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=150,
            height=60,
            command=self.stop_recording
        )
        self.stop_button.grid(row=1, column=0)

    def on_show(self):
        self.start_recording()

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if not self.recording:
            return

        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60

        self.timer_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.after(1000, self.update_timer)  # Repite cada segundo

    def stop_recording(self):
        self.recording = False
        self.parent.show_frame(StartScreen)


class ProfileForm(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.fields = {}
        self.field_keys = {
            "Age": "age",
            "Sex": "sex",
            "Weight (kg)": "weight_(kg)",
            "Height (cm)": "height_(cm)",
            "BMI": "bmi",
            "Neck Circumference (cm)": "neck_circumference_(cm)"
        }
        self.is_editing = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(self, fg_color="gray13")
        title_frame.pack(pady=20)

        try:
            icon = Image.open(ICON_PATH)
            icon = icon.resize((25, 25), Image.Resampling.LANCZOS)
            icon_tk = ctk.CTkImage(light_image=icon, dark_image=icon)
            profile_icon_label = ctk.CTkLabel(title_frame, text="User Profile", image=icon_tk, compound="left", font=ctk.CTkFont(size=20, weight="bold"))
            profile_icon_label.pack()
        except Exception as e:
            print(f"Error loading icon: {e}")
            icon_label = ctk.CTkLabel(title_frame, text="User Profile", font=ctk.CTkFont(size=20, weight="bold"))
            icon_label.pack()

        form_frame = ctk.CTkFrame(self, fg_color="gray13")
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)

        for label in self.field_keys.keys():
            row = ctk.CTkFrame(form_frame)
            row.pack(fill="x", pady=5)

            label_widget = ctk.CTkLabel(row, text=label + ":", width=180, anchor="w")
            label_widget.pack(side="left")

            if label == "Sex":
                entry = ctk.CTkOptionMenu(row, values=["Select an option", "Male", "Female", "Other"])
                entry.set("Select an option")
            else:
                entry = ctk.CTkEntry(row)

            entry.pack(side="left", fill="x", expand=True)
            if label in ["Weight (kg)", "Height (cm)"]:
                entry.bind("<KeyRelease>", lambda event: self.update_bmi())
            self.fields[label] = entry

        self.buttons_frame = ctk.CTkFrame(self, fg_color="gray13")
        self.buttons_frame.pack(pady=10)

        self.edit_save_button = ctk.CTkButton(
            self.buttons_frame, 
            text="Edit", 
            command=self.toggle_edit_save, 
            width=200
        )
        self.edit_save_button.grid(row=0, column=0, padx=10)

        self.cancel_back_button = ctk.CTkButton(
            self.buttons_frame,
            text="Back to Main Menu",
            command=self.cancel_or_back,
            width=200
        )
        self.cancel_back_button.grid(row=0, column=1, padx=10)
        self.cancel_back_button.grid_remove()  # Ocultarlo inicialmente

    def update_bmi(self, *args):
        try:
            weight = float(self.fields["Weight (kg)"].get())
            height = float(self.fields["Height (cm)"].get())

            if 0 < weight <= 500 and 0 < height <= 300:
                bmi = round(weight / ((height / 100) ** 2), 2)
                self.fields["BMI"].configure(state="normal")
                self.fields["BMI"].delete(0, "end")
                self.fields["BMI"].insert(0, str(bmi))
                self.fields["BMI"].configure(state="disabled")
            else:
                raise ValueError
        except ValueError:
            self.fields["BMI"].configure(state="normal")
            self.fields["BMI"].delete(0, "end")
            self.fields["BMI"].insert(0, "")
            self.fields["BMI"].configure(state="disabled")


    def on_show(self):
        self.load_data_into_form()

        if is_profile_complete():
            # Si los datos están completos, iniciar en modo solo lectura
            self.set_fields_state(disabled=True)
            self.edit_save_button.configure(text="Edit")
            self.edit_save_button.grid()
            self.cancel_back_button.configure(text="Back to Main Menu")
            self.cancel_back_button.grid()
            self.is_editing = False
        else:
            # Si los datos están incompletos, iniciar en modo edición
            self.set_fields_state(disabled=False)
            self.edit_save_button.configure(text="Save Data")
            self.edit_save_button.grid()
            self.cancel_back_button.grid_remove()  # Ocultar botón de cancel
            self.is_editing = True

    def load_data_into_form(self):
        data = load_patient_data()
        if not data:
            print("Database is empty. Please enter patient information.")
            return

        for label, entry in self.fields.items():
            key = self.field_keys[label]
            value = data.get(key, "")
            if isinstance(entry, ctk.CTkOptionMenu):
                entry.set(value if value else "Select an option")
            else:
                entry.delete(0, "end")
                entry.insert(0, value)

    def toggle_edit_save(self):
        if not self.is_editing:
            self.set_fields_state(disabled=False)
            self.edit_save_button.configure(text="Save Data")
            self.cancel_back_button.configure(text="Cancel")
            self.is_editing = True
        else:
            data = {}
            for label, widget in self.fields.items():
                key = self.field_keys[label]
                if isinstance(widget, ctk.CTkOptionMenu):
                    value = widget.get()
                    if value == "Select an option":
                        messagebox.showwarning("Input Error", "Please select a valid option for Sex.")
                        return
                    data[key] = value
                else:
                    value = widget.get()
                    if not value.strip():
                        messagebox.showwarning("Input Error", f"Please fill in the {label} field.")
                        return
                    
                    # Validación numérica de los campos específicos
                    if key in ["age", "weight_(kg)", "height_(cm)", "neck_circumference_(cm)"]:
                        try:
                            number = float(value)
                        except ValueError:
                            messagebox.showwarning("Input Error", f"{label} must be a numeric value.")
                            return

                        # Validar los rangos permitidos
                        if key == "age" and not (0 <= number <= 100):
                            messagebox.showwarning("Input Error", "Age must be between 0 and 100.")
                            return
                        if key == "weight_(kg)" and not (0 <= number <= 500):
                            messagebox.showwarning("Input Error", "Weight must be between 0 and 500 kg.")
                            return
                        if key == "height_(cm)" and not (0 <= number <= 300):
                            messagebox.showwarning("Input Error", "Height must be between 0 and 300 cm.")
                            return
                        if key == "neck_circumference_(cm)" and not (0 <= number <= 100):
                            messagebox.showwarning("Input Error", "Neck circumference must be between 0 and 100 cm.")
                            return
                    data[key] = value

            save_patient_data(data)
            messagebox.showinfo("Success", "Patient data saved successfully.")
            # Después de guardar exitosamente
            self.load_data_into_form()
            self.set_fields_state(disabled=True)
            self.edit_save_button.configure(text="Edit")
            self.cancel_back_button.configure(text="Back to Main Menu")
            self.cancel_back_button.grid()
            self.is_editing = False

    def cancel_or_back(self):
        if self.is_editing:
            # Cancelar edición
            self.load_data_into_form()
            self.set_fields_state(disabled=True)
            self.edit_save_button.configure(text="Edit")
            self.cancel_back_button.configure(text="Back to Main Menu")
            self.is_editing = False
        else:
            # Volver al menú
            self.parent.show_frame(StartScreen)

    def set_fields_state(self, disabled=True):
        state = "disabled" if disabled else "normal"
        for widget in self.fields.values():
            widget.configure(state=state)



if __name__ == "__main__":
    app = App()
    app.mainloop()
