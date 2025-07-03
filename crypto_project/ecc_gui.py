# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 09:53:21 2025

@author: karakuzuibrahim
"""

import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Text
import hashlib
from ecies.utils import generate_key
from ecies import encrypt, decrypt

# --- Açık Tema Renkleri ---
BG = "#e8f0fe"         # Açık arka plan
FG = "#2c3e50"         # Koyu yazı rengi
BTN_BG = "#007acc"     # Buton arka planı
BTN_ACTIVE = "#005fa3" # Buton aktif arka planı
FONT = ("Segoe UI", 10)

private_key = None
public_key = None

def generate_keys():
    global private_key, public_key
    key = generate_key()
    private_key = key.to_hex()
    public_key = key.public_key.format(True).hex()
    key_status.config(text="🟢 Anahtar hazır", fg="#50fa7b")
    messagebox.showinfo("Anahtar Oluşturuldu", "ECC anahtar çifti üretildi.")

def save_keys():
    if private_key and public_key:
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, 'w') as f:
                f.write(f"{private_key}\n{public_key}")
            messagebox.showinfo("Kaydedildi", "Anahtarlar kaydedildi.")

def load_keys():
    global private_key, public_key
    path = filedialog.askopenfilename()
    if path:
        with open(path, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                private_key = lines[0]
                public_key = lines[1]
                key_status.config(text="🟢 Anahtar yüklendi", fg="#50fa7b")
                messagebox.showinfo("Yüklendi", "Anahtarlar yüklendi.")

def ecc_encrypt(plaintext):
    if not public_key:
        messagebox.showwarning("Uyarı", "Önce anahtar üretin.")
        return ""
    return encrypt(bytes.fromhex(public_key), plaintext.encode()).hex()

def ecc_decrypt(cipher_hex):
    if not private_key:
        messagebox.showwarning("Uyarı", "Önce anahtar üretin.")
        return ""
    try:
        return decrypt(bytes.fromhex(private_key), bytes.fromhex(cipher_hex)).decode()
    except Exception as e:
        messagebox.showerror("Hata", f"Şifre çözme hatası: {e}")
        return ""

def sha512_hash(text):
    return hashlib.sha512(text.encode()).hexdigest()

def sha512_file(path):
    with open(path, 'rb') as f:
        return hashlib.sha512(f.read()).hexdigest()

def load_file():
    path = filedialog.askopenfilename()
    if path:
        with open(path, 'r', encoding='utf-8') as f:
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, f.read())

def save_output():
    content = output_text.get("1.0", tk.END).strip()
    if content:
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Kaydedildi", "Çıktı kaydedildi.")

def copy_output():
    content = output_text.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        messagebox.showinfo("Panoya Kopyalandı", "Çıktı kopyalandı.")

def show_project_info():
    info_win = Toplevel()
    info_win.title("Proje Bilgisi")
    info_win.geometry("600x400")
    info_win.configure(bg=BG)
    
    info_text = Text(info_win, bg="white", fg=FG, font=FONT, wrap="word")
    info_text.pack(expand=True, fill="both", padx=10, pady=10)
    content = (
        "Bu uygulama ECC (Eliptik Eğri Kriptografisi) ve SHA-512 özet fonksiyonunu kullanarak şifreleme işlemleri yapar.\n\n"
        "Fonksiyonlar:\n"
        "- Anahtar Oluştur / Yükle / Kaydet\n"
        "- ECC Şifreleme / Çözme\n"
        "- SHA512 özetleme (metin/dosya)\n"
        "- Dosya açma, çıktı kaydetme, kopyalama\n"
        "- Açık tema + sol menü arayüzü"
    )
    info_text.insert("1.0", content)
    info_text.config(state="disabled")

def build_gui():
    global root, input_text, output_text, key_status

    root = tk.Tk()
    root.title("ECC + SHA512")
    root.geometry("1000x700")
    root.configure(bg=BG)

    # Sol Menü Çubuğu
    sidebar = tk.Frame(root, bg=BTN_BG, width=200)
    sidebar.pack(side="left", fill="y")

    def menu_button(text, command):
        btn = tk.Button(sidebar, text=text, font=FONT, bg=BTN_BG, fg="white",
                        activebackground=BTN_ACTIVE, activeforeground="white",
                        bd=0, padx=10, pady=10, anchor="w", command=command)
        btn.pack(fill="x")
        return btn

    tk.Label(root, text="ECC + SHA512 Şifreleme Arayüzü", font=("Segoe UI", 18, "bold"), bg=BG, fg=FG).pack(pady=10)

    key_status = tk.Label(root, text="🔴 Anahtar oluşturulmadı", font=FONT, bg=BG, fg="red")
    key_status.pack()

    tk.Label(root, text="Girdi Verisi", font=FONT, bg=BG, fg=FG).pack(anchor="w", padx=210)
    input_text = Text(root, height=6, width=100, font=("Courier New", 10), bg="white", fg="black", insertbackground="black")
    input_text.pack(padx=210, pady=5)

    # Sol menü butonları
    menu_button("🔐 Anahtar Oluştur", generate_keys)
    menu_button("💾 Anahtar Kaydet", save_keys)
    menu_button("📥 Anahtar Yükle", load_keys)
    menu_button("🔒 ECC Şifrele", lambda: [output_text.delete("1.0", tk.END), output_text.insert("1.0", ecc_encrypt(input_text.get("1.0", tk.END).strip()))])
    menu_button("🔓 ECC Çöz", lambda: [output_text.delete("1.0", tk.END), output_text.insert("1.0", ecc_decrypt(input_text.get("1.0", tk.END).strip()))])
    menu_button("🧾 SHA512 (Metin)", lambda: [output_text.delete("1.0", tk.END), output_text.insert("1.0", sha512_hash(input_text.get("1.0", tk.END).strip()))])
    menu_button("📄 SHA512 (Dosya)", lambda: [output_text.delete("1.0", tk.END), output_text.insert("1.0", sha512_file(filedialog.askopenfilename()))])
    menu_button("📂 Dosya Aç", load_file)
    menu_button("💾 Çıktıyı Kaydet", save_output)
    menu_button("📋 Çıktıyı Kopyala", copy_output)
    menu_button("📘 Proje Bilgisi", show_project_info)

    # Çıktı Alanı
    tk.Label(root, text="Çıktı", font=FONT, bg=BG, fg=FG).pack(anchor="w", padx=210, pady=(20, 0))
    output_text = Text(root, height=8, width=100, font=("Courier New", 10), bg="white", fg="black", insertbackground="black")
    output_text.pack(padx=210, pady=5)

    tk.Label(root, text="© İbrahim KARAKUZU | Bilgi Güvenliği ve Kriptografi-ECC & SHA512 GUI", font=("Segoe UI", 10), bg=BG, fg="gray").pack(pady=10)

    root.mainloop()

build_gui()
