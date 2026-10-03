import math
import requests
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

Window.clearcolor = (0.12, 0.16, 0.23, 1) # Warna latar #1E293B

# --- KEYPAD VIRTUAL UNTUK HALAMAN NON-KALKULATOR ---
class VirtualKeypad(GridLayout):
    def __init__(self, get_active_input_func, calculate_func, mode='numeric', **kwargs):
        super().__init__(cols=4, spacing=3, padding=5, size_hint_y=0.45, **kwargs)
        self.get_active_input = get_active_input_func
        self.calculate_func = calculate_func

        if mode == 'hex':
            buttons = [
                'A', 'B', 'C', '⌫',
                'D', 'E', 'F', 'C',
                '7', '8', '9', '=',
                '4', '5', '6', '0',
                '1', '2', '3', '.'
            ]
            self.cols = 4
        else:
            buttons = [
                '7', '8', '9', '⌫',
                '4', '5', '6', 'C',
                '1', '2', '3', '=',
                '0', '00', '.', ''
            ]
            self.cols = 4

        for btn in buttons:
            if not btn:
                self.add_widget(Label())
                continue
            
            if btn == '=':
                b = Button(text=btn, font_size='22sp', background_color=(0.06, 0.72, 0.5, 1), bold=True)
                b.bind(on_release=lambda x: self.calculate_func())
            elif btn == '⌫':
                b = Button(text=btn, font_size='18sp', background_color=(0.39, 0.45, 0.55, 1))
                b.bind(on_release=self.hapus_satu)
            elif btn == 'C':
                b = Button(text=btn, font_size='18sp', background_color=(0.93, 0.26, 0.26, 1))
                b.bind(on_release=self.hapus_semua)
            else:
                b = Button(text=btn, font_size='18sp', background_color=(0.2, 0.25, 0.33, 1), bold=True)
                b.bind(on_release=lambda instance, val=btn: self.ketik(val))
            
            self.add_widget(b)

    def ketik(self, val):
        inp = self.get_active_input()
        if inp:
            inp.text += val

    def hapus_satu(self, instance):
        inp = self.get_active_input()
        if inp and len(inp.text) > 0:
            inp.text = inp.text[:-1]

    def hapus_semua(self, instance):
        inp = self.get_active_input()
        if inp:
            inp.text = ''

# --- POPUP SIDEBAR MENU (DAFTAR LENGKAP) ---
class SidebarMenu(ModalView):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.75, 1)
        self.pos_hint = {'x': 0, 'y': 0}
        self.background_color = (0.06, 0.09, 0.16, 0.95)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        layout.add_widget(Label(
            text="MENU UTAMA", font_size='18sp', bold=True,
            size_hint_y=None, height='40dp', color=(1, 1, 1, 1)
        ))

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        content.bind(minimum_height=content.setter('height'))

        menu_items = [
            ("Favorit", True),
            ("🧮 Kalkulator", "kalkulator"),
            ("💱 Mata Uang", "mata_uang"),
            ("📏 Satuan", "satuan"),
            ("🏷️ Diskon", "diskon"),
            ("💳 Pinjaman", "pinjaman"),
            ("Semua Kalkulator", True),
            ("🔢 Angka Heksadesimal", "heksadesimal"),
            ("⛽ Biaya Bahan Bakar", "biaya_bbm"),
            ("🚗 Efisiensi Bahan Bakar", "efisiensi_bbm"),
            ("⚖️ Harga Satuan", "harga_satuan"),
            ("🎓 IPK", "ipk"),
            ("🩺 Kesehatan (BMI)", "kesehatan"),
            ("📊 Pajak Penjualan", "pajak"),
            ("💰 Tabungan", "tabungan"),
            ("Pengaturan", True),
            ("⚙️ Pengaturan", "pengaturan"),
            ("❓ Kiat Penggunaan", "kiat")
        ]

        for label, target in menu_items:
            if target is True:
                lbl = Label(
                    text=label, font_size='14sp', bold=True,
                    color=(0.22, 0.74, 0.97, 1), size_hint_y=None, height='35dp', halign='left'
                )
                lbl.bind(size=lbl.setter('text_size'))
                content.add_widget(lbl)
            else:
                btn = Button(
                    text=f"  {label}", font_size='14sp',
                    background_color=(0.12, 0.16, 0.23, 1),
                    size_hint_y=None, height='45dp', halign='left'
                )
                btn.bind(size=btn.setter('text_size'))
                btn.bind(on_release=lambda x, t=target: self.pilih_menu(sm, t))
                content.add_widget(btn)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        btn_close = Button(
            text="✖ Tutup Menu", size_hint_y=None, height='45dp',
            background_color=(0.93, 0.26, 0.26, 1), bold=True
        )
        btn_close.bind(on_release=self.dismiss)
        layout.add_widget(btn_close)

        self.add_widget(layout)

    def pilih_menu(self, sm, target):
        self.dismiss()
        sm.current = target

# --- HEADER BAR DENGAN TOMBOL ☰ MENU ---
class HeaderBar(BoxLayout):
    def __init__(self, sm, judul, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '50dp'
        self.padding = [5, 5, 5, 5]
        self.spacing = 10

        btn_menu = Button(
            text="☰ Menu", size_hint_x=None, width='90dp',
            background_color=(0.2, 0.25, 0.33, 1), bold=True
        )
        btn_menu.bind(on_release=lambda x: SidebarMenu(sm).open())

        lbl_title = Label(
            text=judul, font_size='18sp', bold=True,
            halign='left', color=(1, 1, 1, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))

        self.add_widget(btn_menu)
        self.add_widget(lbl_title)

# --- 1. KALKULATOR STANDAR ---
class KalkulatorScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(HeaderBar(sm, "Kalkulator Standar"))

        self.display = TextInput(
            text='', font_size='32sp', readonly=True,
            halign='right', multiline=False,
            size_hint_y=0.25, background_color=(0.97, 0.98, 0.99, 1)
        )
        layout.add_widget(self.display)

        grid = GridLayout(cols=4, spacing=2, padding=5)
        buttons = [
            'C', '(', ')', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '00', '.', '='
        ]

        for btn in buttons:
            if btn == '=':
                b = Button(text=btn, font_size='24sp', background_color=(0.06, 0.72, 0.5, 1))
                b.bind(on_release=self.hitung)
            elif btn == 'C':
                b = Button(text=btn, font_size='20sp', background_color=(0.93, 0.26, 0.26, 1))
                b.bind(on_release=self.clear)
            else:
                b = Button(text=btn, font_size='20sp', background_color=(0.2, 0.25, 0.33, 1))
                b.bind(on_release=self.tekan)
            grid.add_widget(b)

        layout.add_widget(grid)
        self.add_widget(layout)

    def tekan(self, instance):
        self.display.text += instance.text

    def clear(self, instance):
        self.display.text = ''

    def hitung(self, instance):
        try:
            self.display.text = str(eval(self.display.text))
        except Exception:
            self.display.text = "Error"

# --- 2. KONVERSI MATA UANG ---
class MataUangScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Konversi Mata Uang"))

        row_curr = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', spacing=10)
        list_curr = ["USD", "IDR", "EUR", "JPY", "SGD", "MYR", "SAR", "AUD", "KRW", "GBP", "CNY", "THB"]

        self.sp_dari = Spinner(text='USD', values=list_curr)
        self.sp_ke = Spinner(text='IDR', values=list_curr)
        btn_tukar = Button(text='⇄', size_hint_x=None, width='50dp', background_color=(0.23, 0.51, 0.96, 1))
        btn_tukar.bind(on_release=self.tukar_val)

        row_curr.add_widget(self.sp_dari)
        row_curr.add_widget(btn_tukar)
        row_curr.add_widget(self.sp_ke)
        layout.add_widget(row_curr)

        self.txt_nominal = TextInput(hint_text="Masukkan Nominal", multiline=False, size_hint_y=None, height='45dp', font_size='18sp')
        layout.add_widget(self.txt_nominal)

        self.lbl_kurs = Label(text="Info Kurs: -", font_size='13sp', color=(0.98, 0.75, 0.14, 1), size_hint_y=None, height='25dp')
        layout.add_widget(self.lbl_kurs)

        self.lbl_hasil = Label(text="Hasil:\n-", font_size='18sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.txt_nominal,
            calculate_func=self.proses_konversi
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def tukar_val(self, instance):
        dari, ke = self.sp_dari.text, self.sp_ke.text
        self.sp_dari.text, self.sp_ke.text = ke, dari

    def proses_konversi(self):
        threading.Thread(target=self._fetch_kurs).start()

    def _fetch_kurs(self):
        try:
            d, k = self.sp_dari.text, self.sp_ke.text
            res = requests.get(f"https://open.er-api.com/v6/latest/{d}", timeout=5).json()
            rate = res['rates'][k]

            text_kurs = f"Info Kurs: 1 {d} = {rate:,.2f} {k}"
            if self.txt_nominal.text.strip():
                val = float(self.txt_nominal.text)
                hasil = val * rate
                text_hasil = f"Hasil ({k}):\n{hasil:,.2f}"
            else:
                text_hasil = "Hasil:\n-"
        except Exception:
            text_kurs = "Info Kurs: -"
            text_hasil = "Gagal Koneksi / Input Salah"

        Clock.schedule_once(lambda dt: self._update_ui(text_kurs, text_hasil))

    def _update_ui(self, text_kurs, text_hasil):
        self.lbl_kurs.text = text_kurs
        self.lbl_hasil.text = text_hasil

# --- 3. KONVERSI SATUAN ---
class SatuanScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Konversi Satuan"))

        self.data_satuan = {
            "Panjang": {"Meter (m)": 1.0, "Kilometer (km)": 1000.0, "Sentimeter (cm)": 0.01, "Milimeter (mm)": 0.001, "Inci (in)": 0.0254, "Kaki (ft)": 0.3048, "Mil (mi)": 1609.34},
            "Berat / Massa": {"Kilogram (kg)": 1.0, "Gram (g)": 0.001, "Miligram (mg)": 0.000001, "Ton": 1000.0, "Pon (lbs)": 0.453592, "Oons (oz)": 0.0283495},
            "Suhu": {"Celsius (°C)": "C", "Fahrenheit (°F)": "F", "Kelvin (K)": "K", "Reamur (°R)": "R"}
        }

        self.sp_kategori = Spinner(text='Panjang', values=list(self.data_satuan.keys()), size_hint_y=None, height='40dp', background_color=(0.2, 0.25, 0.33, 1))
        self.sp_kategori.bind(text=self.ganti_kategori)
        layout.add_widget(self.sp_kategori)

        row_unit = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', spacing=8)
        self.sp_dari = Spinner(text='', values=[], background_color=(0.15, 0.2, 0.28, 1))
        self.sp_ke = Spinner(text='', values=[], background_color=(0.15, 0.2, 0.28, 1))
        
        btn_tukar = Button(text='⇄', size_hint_x=None, width='50dp', background_color=(0.23, 0.51, 0.96, 1))
        btn_tukar.bind(on_release=self.tukar_val)

        row_unit.add_widget(self.sp_dari)
        row_unit.add_widget(btn_tukar)
        row_unit.add_widget(self.sp_ke)
        layout.add_widget(row_unit)

        self.txt_nominal = TextInput(hint_text="Masukkan Nilai", multiline=False, size_hint_y=None, height='45dp', font_size='18sp')
        layout.add_widget(self.txt_nominal)

        self.lbl_hasil = Label(text="Hasil:\n-", font_size='18sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        self.ganti_kategori(None, 'Panjang')

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.txt_nominal,
            calculate_func=self.hitung_konversi
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def ganti_kategori(self, instance, kat):
        units = list(self.data_satuan[kat].keys())
        self.sp_dari.values = units
        self.sp_ke.values = units
        self.sp_dari.text = units[0]
        self.sp_ke.text = units[1] if len(units) > 1 else units[0]
        self.lbl_hasil.text = "Hasil:\n-"

    def tukar_val(self, instance):
        d, k = self.sp_dari.text, self.sp_ke.text
        self.sp_dari.text, self.sp_ke.text = k, d

    def hitung_konversi(self):
        if not self.txt_nominal.text.strip():
            self.lbl_hasil.text = "Hasil:\n-"
            return

        try:
            val = float(self.txt_nominal.text)
            kat = self.sp_kategori.text
            dari = self.sp_dari.text
            ke = self.sp_ke.text

            if kat == "Suhu":
                hasil = self._konversi_suhu(val, self.data_satuan[kat][dari], self.data_satuan[kat][ke])
            else:
                base_val = val * self.data_satuan[kat][dari]
                hasil = base_val / self.data_satuan[kat][ke]

            self.lbl_hasil.text = f"Hasil ({ke}):\n{hasil:,.4f}".rstrip('0').rstrip('.')
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

    def _konversi_suhu(self, val, unit_dari, unit_ke):
        if unit_dari == 'C': c = val
        elif unit_dari == 'F': c = (val - 32) * 5/9
        elif unit_dari == 'K': c = val - 273.15
        elif unit_dari == 'R': c = val * 5/4

        if unit_ke == 'C': return c
        elif unit_ke == 'F': return (c * 9/5) + 32
        elif unit_ke == 'K': return c + 273.15
        elif unit_ke == 'R': return c * 4/5

# --- 4. KALKULATOR DISKON ---
class DiskonScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Kalkulator Diskon"))

        self.txt_harga = TextInput(hint_text="Harga Asli (Rp)", multiline=False, size_hint_y=None, height='45dp')
        self.txt_diskon = TextInput(hint_text="Diskon (%)", multiline=False, size_hint_y=None, height='45dp')

        self.txt_harga.bind(focus=self.on_focus)
        self.txt_diskon.bind(focus=self.on_focus)

        layout.add_widget(self.txt_harga)
        layout.add_widget(self.txt_diskon)

        self.lbl_hasil = Label(text="Hasil Akhir:\n-", font_size='18sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_harga,
            calculate_func=self.hitung_diskon
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung_diskon(self):
        try:
            h = float(self.txt_harga.text)
            d = float(self.txt_diskon.text)
            potongan = h * (d / 100)
            akhir = h - potongan
            self.lbl_hasil.text = f"Potongan: Rp {potongan:,.0f}\nHarga Akhir: Rp {akhir:,.0f}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 5. KALKULATOR PINJAMAN ---
class PinjamanScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Kalkulator Pinjaman"))

        self.txt_pinjaman = TextInput(hint_text="Jumlah Pinjaman (Rp)", multiline=False, size_hint_y=None, height='40dp')
        self.txt_bunga = TextInput(hint_text="Bunga Per Tahun (%)", multiline=False, size_hint_y=None, height='40dp')
        self.txt_tenor = TextInput(hint_text="Tenor (Bulan)", multiline=False, size_hint_y=None, height='40dp')

        for txt in [self.txt_pinjaman, self.txt_bunga, self.txt_tenor]:
            txt.bind(focus=self.on_focus)
            layout.add_widget(txt)

        self.lbl_hasil = Label(text="Cicilan Per Bulan:\n-", font_size='16sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_pinjaman,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            p = float(self.txt_pinjaman.text)
            r = float(self.txt_bunga.text) / 100 / 12
            n = float(self.txt_tenor.text)

            if r == 0:
                cicilan = p / n
            else:
                cicilan = p * (r * (1 + r)**n) / ((1 + r)**n - 1)

            total_bayar = cicilan * n
            self.lbl_hasil.text = f"Cicilan: Rp {cicilan:,.0f}/bln\nTotal Bayar: Rp {total_bayar:,.0f}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 6. ANGKA HEKSADESIMAL & KONVERSI BASIS ---
class HeksadesimalScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Konversi Basis (Hex/Dec/Bin)"))

        self.sp_mode = Spinner(text='Desimal', values=['Desimal', 'Heksadesimal', 'Biner'], size_hint_y=None, height='40dp')
        layout.add_widget(self.sp_mode)

        self.txt_val = TextInput(hint_text="Masukkan Angka Asal", multiline=False, size_hint_y=None, height='45dp')
        layout.add_widget(self.txt_val)

        self.lbl_hasil = Label(text="Hasil Konversi:\n-", font_size='15sp', bold=True, halign='center', size_hint_y=0.25)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.txt_val,
            calculate_func=self.hitung,
            mode='hex'
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def hitung(self):
        txt = self.txt_val.text.strip()
        mode = self.sp_mode.text
        if not txt:
            self.lbl_hasil.text = "Hasil Konversi:\n-"
            return

        try:
            if mode == 'Desimal':
                d = int(txt)
            elif mode == 'Heksadesimal':
                d = int(txt, 16)
            elif mode == 'Biner':
                d = int(txt, 2)

            self.lbl_hasil.text = f"Dec: {d}\nHex: {hex(d)[2:].upper()}\nBin: {bin(d)[2:]}"
        except Exception:
            self.lbl_hasil.text = "Format Angka Tidak Valid!"

# --- 7. BIAYA BAHAN BAKAR ---
class BiayaBBMScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Biaya Bahan Bakar"))

        self.txt_jarak = TextInput(hint_text="Jarak Tempuh (km)", multiline=False, size_hint_y=None, height='40dp')
        self.txt_konsumsi = TextInput(hint_text="Konsumsi BBM (km/liter)", multiline=False, size_hint_y=None, height='40dp')
        self.txt_harga = TextInput(hint_text="Harga BBM Per Liter (Rp)", multiline=False, size_hint_y=None, height='40dp')

        for txt in [self.txt_jarak, self.txt_konsumsi, self.txt_harga]:
            txt.bind(focus=self.on_focus)
            layout.add_widget(txt)

        self.lbl_hasil = Label(text="Total Biaya:\n-", font_size='16sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_jarak,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            j = float(self.txt_jarak.text)
            k = float(self.txt_konsumsi.text)
            h = float(self.txt_harga.text)

            liter = j / k
            biaya = liter * h
            self.lbl_hasil.text = f"Kebutuhan BBM: {liter:,.2f} Liter\nTotal Biaya: Rp {biaya:,.0f}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 8. EFISIENSI BAHAN BAKAR ---
class EfisiensiBBMScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Efisiensi Bahan Bakar"))

        self.txt_jarak = TextInput(hint_text="Jarak Tempuh (km)", multiline=False, size_hint_y=None, height='45dp')
        self.txt_bensin = TextInput(hint_text="BBM Terpakai (Liter)", multiline=False, size_hint_y=None, height='45dp')

        self.txt_jarak.bind(focus=self.on_focus)
        self.txt_bensin.bind(focus=self.on_focus)

        layout.add_widget(self.txt_jarak)
        layout.add_widget(self.txt_bensin)

        self.lbl_hasil = Label(text="Efisiensi:\n-", font_size='16sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_jarak,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            j = float(self.txt_jarak.text)
            l = float(self.txt_bensin.text)

            kml = j / l
            l100 = (l / j) * 100
            self.lbl_hasil.text = f"Efisiensi: {kml:,.2f} km/L\n({l100:,.2f} L/100km)"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 9. HARGA SATUAN ---
class HargaSatuanScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Perbandingan Harga Satuan"))

        self.txt_h1 = TextInput(hint_text="Harga Produk A (Rp)", multiline=False, size_hint_y=None, height='35dp')
        self.txt_u1 = TextInput(hint_text="Jumlah/Berat A (gram/ml/pcs)", multiline=False, size_hint_y=None, height='35dp')
        self.txt_h2 = TextInput(hint_text="Harga Produk B (Rp)", multiline=False, size_hint_y=None, height='35dp')
        self.txt_u2 = TextInput(hint_text="Jumlah/Berat B (gram/ml/pcs)", multiline=False, size_hint_y=None, height='35dp')

        for txt in [self.txt_h1, self.txt_u1, self.txt_h2, self.txt_u2]:
            txt.bind(focus=self.on_focus)
            layout.add_widget(txt)

        self.lbl_hasil = Label(text="Hasil Perbandingan:\n-", font_size='14sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_h1,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            h1, u1 = float(self.txt_h1.text), float(self.txt_u1.text)
            h2, u2 = float(self.txt_h2.text), float(self.txt_u2.text)

            r1 = h1 / u1
            r2 = h2 / u2

            txt_a = f"A: Rp {r1:,.2f}/unit"
            txt_b = f"B: Rp {r2:,.2f}/unit"

            if r1 < r2:
                rekom = "Produk A LEBIH MURAH!"
            elif r2 < r1:
                rekom = "Produk B LEBIH MURAH!"
            else:
                rekom = "Harga Satuan SAMA!"

            self.lbl_hasil.text = f"{txt_a} | {txt_b}\n{rekom}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 10. KALKULATOR IPK ---
class IPKScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Kalkulator IPK Semester"))

        self.txt_sks = TextInput(hint_text="Total SKS Diambil", multiline=False, size_hint_y=None, height='45dp')
        self.txt_poin = TextInput(hint_text="Total Mutu/Poin (SKS x Bobot)", multiline=False, size_hint_y=None, height='45dp')

        self.txt_sks.bind(focus=self.on_focus)
        self.txt_poin.bind(focus=self.on_focus)

        layout.add_widget(self.txt_sks)
        layout.add_widget(self.txt_poin)

        self.lbl_hasil = Label(text="IPK:\n-", font_size='18sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_sks,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            sks = float(self.txt_sks.text)
            poin = float(self.txt_poin.text)

            ipk = poin / sks
            self.lbl_hasil.text = f"Indeks Prestasi Kumulatif (IPK):\n{ipk:.2f}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 11. KESEHATAN (BMI) ---
class KesehatanScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Kalkulator Kesehatan (BMI)"))

        self.txt_tb = TextInput(hint_text="Tinggi Badan (cm)", multiline=False, size_hint_y=None, height='45dp')
        self.txt_bb = TextInput(hint_text="Berat Badan (kg)", multiline=False, size_hint_y=None, height='45dp')

        self.txt_tb.bind(focus=self.on_focus)
        self.txt_bb.bind(focus=self.on_focus)

        layout.add_widget(self.txt_tb)
        layout.add_widget(self.txt_bb)

        self.lbl_hasil = Label(text="Hasil BMI:\n-", font_size='16sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_tb,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            tb = float(self.txt_tb.text) / 100
            bb = float(self.txt_bb.text)

            bmi = bb / (tb * tb)
            if bmi < 18.5:
                status = "Kekurangan Berat Badan"
            elif 18.5 <= bmi < 24.9:
                status = "Normal / Ideal"
            elif 25 <= bmi < 29.9:
                status = "Kelebihan Berat Badan"
            else:
                status = "Obesitas"

            self.lbl_hasil.text = f"Indeks BMI: {bmi:.1f}\nKategori: {status}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 12. PAJAK PENJUALAN ---
class PajakScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Kalkulator Pajak Penjualan"))

        self.txt_harga = TextInput(hint_text="Harga Sebelum Pajak (Rp)", multiline=False, size_hint_y=None, height='45dp')
        self.txt_pajak = TextInput(hint_text="Tarif Pajak / PPN (%)", multiline=False, size_hint_y=None, height='45dp')

        self.txt_harga.bind(focus=self.on_focus)
        self.txt_pajak.bind(focus=self.on_focus)

        layout.add_widget(self.txt_harga)
        layout.add_widget(self.txt_pajak)

        self.lbl_hasil = Label(text="Total Bayar:\n-", font_size='16sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_harga,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            h = float(self.txt_harga.text)
            p = float(self.txt_pajak.text)

            nominal_pajak = h * (p / 100)
            total = h + nominal_pajak
            self.lbl_hasil.text = f"Pajak: Rp {nominal_pajak:,.0f}\nTotal Akhir: Rp {total:,.0f}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 13. KALKULATOR TABUNGAN ---
class TabunganScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        self.active_input = None
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        layout.add_widget(HeaderBar(sm, "Kalkulator Tabungan Bunga"))

        self.txt_awal = TextInput(hint_text="Setoran Awal (Rp)", multiline=False, size_hint_y=None, height='40dp')
        self.txt_bunga = TextInput(hint_text="Bunga Per Tahun (%)", multiline=False, size_hint_y=None, height='40dp')
        self.txt_tahun = TextInput(hint_text="Lama Menabung (Tahun)", multiline=False, size_hint_y=None, height='40dp')

        for txt in [self.txt_awal, self.txt_bunga, self.txt_tahun]:
            txt.bind(focus=self.on_focus)
            layout.add_widget(txt)

        self.lbl_hasil = Label(text="Hasil Tabungan:\n-", font_size='16sp', bold=True, halign='center', size_hint_y=0.2)
        layout.add_widget(self.lbl_hasil)

        keypad = VirtualKeypad(
            get_active_input_func=lambda: self.active_input or self.txt_awal,
            calculate_func=self.hitung
        )
        layout.add_widget(keypad)

        self.add_widget(layout)

    def on_focus(self, instance, value):
        if value:
            self.active_input = instance

    def hitung(self):
        try:
            p = float(self.txt_awal.text)
            r = float(self.txt_bunga.text) / 100
            t = float(self.txt_tahun.text)

            total = p * ((1 + r)**t)
            profit = total - p
            self.lbl_hasil.text = f"Bunga Diterima: Rp {profit:,.0f}\nTotal Tabungan Akhir: Rp {total:,.0f}"
        except Exception:
            self.lbl_hasil.text = "Masukkan Angka Valid"

# --- 14. PENGATURAN ---
class PengaturanScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(HeaderBar(sm, "Pengaturan Application"))

        layout.add_widget(Label(text="Tema Tampilan", font_size='16sp', bold=True, size_hint_y=None, height='30dp'))
        
        btn_dark = Button(text="Mode Gelap (Default)", size_hint_y=None, height='45dp', background_color=(0.2, 0.25, 0.33, 1))
        btn_dark.bind(on_release=lambda x: self.set_theme((0.12, 0.16, 0.23, 1)))

        btn_blue = Button(text="Mode Navy Modern", size_hint_y=None, height='45dp', background_color=(0.09, 0.14, 0.23, 1))
        btn_blue.bind(on_release=lambda x: self.set_theme((0.07, 0.12, 0.2, 1)))

        layout.add_widget(btn_dark)
        layout.add_widget(btn_blue)

        layout.add_widget(Label(text="Informasi Versi", font_size='16sp', bold=True, size_hint_y=None, height='40dp'))
        layout.add_widget(Label(text="Kalkulator Serbaguna v2.0\nDikembangkan untuk Pydroid 3 / Kivy", halign='center'))

        self.add_widget(layout)

    def set_theme(self, color):
        Window.clearcolor = color

# --- 15. KIAT PENGGUNAAN ---
class KiatScreen(Screen):
    def __init__(self, sm, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(HeaderBar(sm, "Kiat Penggunaan"))

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        content.bind(minimum_height=content.setter('height'))

        panduan = [
            ("📱 Navigasi Aplikasi", "Ketuk '☰ Menu' di pojok kiri atas untuk beralih antar fitur kalkulator."),
            ("🧮 Kalkulator Standar", "Mendukung perhitungan aritmatika langsung."),
            ("💱 Mata Uang", "Diperbarui secara langsung jika HP terhubung ke internet."),
            ("🔢 Heksadesimal", "Mendukung konversi langsung antara Desimal, Biner, dan Hexa."),
            ("⌨️ Keyboard Virtual", "Gunakan tombol angka yang ada di bagian bawah layar tanpa perlu membuka keyboard HP.")
        ]

        for judul, isi in panduan:
            content.add_widget(Label(text=judul, font_size='16sp', bold=True, color=(0.22, 0.74, 0.97, 1), size_hint_y=None, height='30dp', halign='left'))
            lbl_isi = Label(text=isi, font_size='14sp', size_hint_y=None, halign='left')
            lbl_isi.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            lbl_isi.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            content.add_widget(lbl_isi)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

# --- APP UTAMA ---
class KalkulatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(KalkulatorScreen(sm, name='kalkulator'))
        sm.add_widget(MataUangScreen(sm, name='mata_uang'))
        sm.add_widget(SatuanScreen(sm, name='satuan'))
        sm.add_widget(DiskonScreen(sm, name='diskon'))
        sm.add_widget(PinjamanScreen(sm, name='pinjaman'))
        sm.add_widget(HeksadesimalScreen(sm, name='heksadesimal'))
        sm.add_widget(BiayaBBMScreen(sm, name='biaya_bbm'))
        sm.add_widget(EfisiensiBBMScreen(sm, name='efisiensi_bbm'))
        sm.add_widget(HargaSatuanScreen(sm, name='harga_satuan'))
        sm.add_widget(IPKScreen(sm, name='ipk'))
        sm.add_widget(KesehatanScreen(sm, name='kesehatan'))
        sm.add_widget(PajakScreen(sm, name='pajak'))
        sm.add_widget(TabunganScreen(sm, name='tabungan'))
        sm.add_widget(PengaturanScreen(sm, name='pengaturan'))
        sm.add_widget(KiatScreen(sm, name='kiat'))
        return sm

if __name__ == '__main__':
    KalkulatorApp().run()