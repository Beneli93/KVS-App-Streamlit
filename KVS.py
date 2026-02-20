import streamlit as st
import json
import os
import pandas as pd
import time
import uuid
from datetime import datetime, timedelta

# === 1. SEITEN-KONFIGURATION ===
st.set_page_config(page_title="KVS Pro", layout="wide", page_icon="👥")

# === 2. DARK-MODE DESIGN & STYLING (CSS) ===
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2e004f, #4a148c);
        padding-top: 20px;
        border-right: 1px solid #333;
    }
    .stButton > button {
        width: 100%; border-radius: 10px; height: 3em;
        background-color: rgba(255, 255, 255, 0.05); color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
    }
    .stButton > button:hover { background-color: #6a1b9a; border: 1px solid #8e24aa; }
    h1, h2, h3 { color: #bb86fc; font-weight: 800; }
    .block-container { max-width: 1200px; padding-top: 2rem; }
    [data-testid="stMetricValue"] { color: #bb86fc !important; }
    .reminder-card { background-color: #1d2129; padding: 12px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 8px; }
    .focus-card { background-color: #262730; padding: 25px; border-radius: 15px; border: 3px solid #bb86fc; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# === 3. DATENMODELLE & LOGIK ===
class Kunde:
    def __init__(self, anrede, vorname, nachname, geschlecht, alter, email, wohnorte, plz="", telefon="", mobil="", kunden_id=None, termine=None):
        self.kunden_id = kunden_id or str(uuid.uuid4())[:8]
        self.anrede = anrede
        self.vorname = vorname
        self.nachname = nachname
        self.geschlecht = geschlecht
        self.alter = alter
        self.email = email
        self.plz = plz
        self.telefon = telefon
        self.mobil = mobil
        self.wohnorte = wohnorte if isinstance(wohnorte, list) else [wohnorte]
        self.termine = termine if isinstance(termine, list) else []

    def to_dict(self):
        return {
            "ID": self.kunden_id, "Anrede": self.anrede, "Vorname": self.vorname, 
            "Nachname": self.nachname, "Geschlecht": self.geschlecht, "Alter": self.alter,
            "E-Mail": self.email, "PLZ": self.plz, "Telefon": self.telefon, "Mobil": self.mobil,
            "Wohnorte": ", ".join(self.wohnorte), "Termine": " | ".join(self.termine)
        }

    def to_table_row(self):
        return {
            "ID": self.kunden_id, "Anrede": self.anrede, "Nachname": self.nachname, "Vorname": self.vorname,
            "Geschlecht": self.geschlecht, "Alter": self.alter, "Mobil": self.mobil, "Telefon": self.telefon, 
            "E-Mail": self.email, "Wohnort": ", ".join(self.wohnorte), "PLZ": self.plz, "Termine vorhanden?": "Ja" if self.termine else "Nein"
        }

    @staticmethod
    def from_dict(data):
        return Kunde(
            kunden_id=data.get("ID"), anrede=data.get("Anrede", ""), vorname=data.get("Vorname", ""),
            nachname=data.get("Nachname", ""), geschlecht=data.get("Geschlecht", ""),
            alter=data.get("Alter", 1), email=data.get("E-Mail", ""), plz=data.get("PLZ", ""),
            telefon=data.get("Telefon", ""), mobil=data.get("Mobil", ""), 
            wohnorte=data.get("Wohnorte", "").split(", ") if data.get("Wohnorte") else [],
            termine=data.get("Termine", "").split(" | ") if data.get("Termine") else []
        )

class Datenbank:
    def __init__(self):
        self.kunden = {}
    def hinzufuegen(self, kunde):
        self.kunden[kunde.kunden_id] = kunde
    def bearbeiten(self, kunden_id, **kwargs):
        if kunden_id in self.kunden:
            for key, value in kwargs.items():
                if hasattr(self.kunden[kunden_id], key):
                    setattr(self.kunden[kunden_id], key, value)
    def loeschen(self, kunden_id):
        self.kunden.pop(kunden_id, None)

def speichern(db, datei="kunden.json"):
    with open(datei, "w") as f:
        json.dump({k_id: k.to_dict() for k_id, k in db.kunden.items()}, f, indent=4)

def laden(datei="kunden.json"):
    db = Datenbank()
    if os.path.exists(datei):
        with open(datei, "r") as f:
            try:
                daten = json.load(f)
                for info in daten.values():
                    db.hinzufuegen(Kunde.from_dict(info))
            except: pass
    return db

# === 4. HAUPT-INTERFACE ===
def main():
    if 'db' not in st.session_state:
        st.session_state.db = laden()
    db = st.session_state.db

    if 'page' not in st.session_state: st.session_state.page = "Startseite"
    if 'edit_id' not in st.session_state: st.session_state.edit_id = None
    if 'edit_term_idx' not in st.session_state: st.session_state.edit_term_idx = None
    if 'delete_confirm' not in st.session_state: st.session_state.delete_confirm = False
    if 'reset_stamm_search' not in st.session_state: st.session_state.reset_stamm_search = False
    if 'reset_overview_search' not in st.session_state: st.session_state.reset_overview_search = False
    if 'reset_book_search' not in st.session_state: st.session_state.reset_book_search = False

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.markdown("# 🚀 KVS Menü")
    if st.sidebar.button("🏠 Startseite", use_container_width=True):
        st.session_state.page = "Startseite"; st.session_state.edit_id = None; st.rerun()
    if st.sidebar.button("📅 Termine", use_container_width=True):
        st.session_state.page = "Termine"; st.rerun()
    if st.sidebar.button("📑 Kundenstamm", use_container_width=True):
        st.session_state.page = "Kundenstamm"; st.session_state.edit_id = None; st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"Kunden im System: **{len(db.kunden)}**")

    # --- STARTSEITE ---
    if st.session_state.page == "Startseite":
        st.title("🏠 KVS KundenVerwaltungsSystem")
        c1, c2, c3 = st.columns(3)
        c1.metric("Gesamt-Kunden", len(db.kunden))
        alts = [int(k.alter) for k in db.kunden.values() if str(k.alter).isdigit() and int(k.alter) > 0]
        c2.metric("Ø-Alter", f"{sum(alts)/len(alts):.1f} J." if alts else "0 J.")
        c3.metric("Status", "Online")
        st.markdown("---")
        
        st.subheader("💡 Schnellzugriff")
        q1, q2 = st.columns(2)
        if q1.button("👤 Kunden Anlegen", use_container_width=True):
            st.session_state.page = "Kundenstamm"; st.rerun()
        if q2.button("📅 Termin buchen", use_container_width=True):
            st.session_state.page = "Termine"; st.rerun()
        
        st.markdown("---")
        
        heute = datetime.now()
        alle_termine = []
        for k in db.kunden.values():
            for idx, t_str in enumerate(k.termine):
                try:
                    p = t_str.split(" um "); d_dt = datetime.strptime(p[0], '%d.%m.%Y')
                    p2 = p[1].split(" - "); t_dt = datetime.strptime(p2[0], '%H:%M').time()
                    full_dt = datetime.combine(d_dt.date(), t_dt)
                    if full_dt >= heute:
                        alle_termine.append({"dt": full_dt, "kunde": k, "note": p2[1] if len(p2)>1 else ""})
                except: pass
        alle_termine.sort(key=lambda x: x['dt'])

        st.subheader("📌 Nächster Termin")
        if alle_termine:
            nt = alle_termine[0]; kn = nt['kunde']
            st.markdown(f"""
            <div class="focus-card">
                <h2 style="color: #bb86fc; margin-top:0;">📅 {nt['dt'].strftime('%d.%m.%Y um %H:%M Uhr')}</h2>
                <p style="font-size: 1.4rem; margin-bottom:10px;"><b>{kn.anrede} {kn.vorname} {kn.nachname}</b></p>
                <p style="font-size: 1.1rem;">📞 <b>Telefon:</b> {kn.telefon} | 📱 <b>Mobil:</b> {kn.mobil}</p>
                <p style="font-size: 1.1rem; background: #1d2129; padding: 10px; border-radius: 5px;">📝 <b>Notiz:</b> {nt['note']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🔔 Kommende Termine (7 Tage)")
        bevor_7 = [t for t in alle_termine if t['dt'] <= heute + timedelta(days=7)]
        if bevor_7:
            for it in bevor_7:
                k = it['kunde']
                st.markdown(f'<div class="reminder-card">📅 {it["dt"].strftime("%d.%m.%Y | %H:%M")} | <b>{k.nachname}</b> (Tel: {k.telefon})<br>{it["note"]}</div>', unsafe_allow_html=True)
        else: st.info("Keine weiteren Termine.")

    # --- TERMINE ---
    elif st.session_state.page == "Termine":
        st.title("📅 Terminverwaltung")
        tab1, tab2 = st.tabs(["Termin buchen", "Terminsuche & Bearbeitung"])

        with tab1:
            st.subheader("Neuen Termin anlegen")
            if st.session_state.reset_book_search:
                st.session_state.reset_book_search = False
                st.session_state.term_book_search = ""
                st.rerun()

            search_t = st.text_input("🔍 Kunde suchen", key="term_book_search")
            sel_k_id = None
            if search_t:
                hits = [k for k in db.kunden.values() if any(search_t.lower() in str(v).lower() for v in [k.vorname, k.nachname, k.kunden_id])]
                if hits:
                    sel_k = st.selectbox(
                        "Kunde wählen", hits, index=None,
                        placeholder="Bitte Kunden auswählen...",
                        format_func=lambda x: f"{x.nachname}, {x.vorname} ({x.kunden_id})",
                        key="book_select"
                    )
                    if sel_k:
                        sel_k_id = sel_k.kunden_id  # Speichere nur die ID
                        if st.button("❌ Schließen", key="btn_close_book"):
                            st.session_state.reset_book_search = True
                            st.rerun()

            with st.form("term_form_new"):
                c1, c2 = st.columns(2)
                d = c1.date_input("Datum", datetime.now())
                t = c2.time_input("Uhrzeit", datetime.now().time())
                ctel, cmob = st.columns(2)
                t_val = ctel.text_input("Telefon", value=db.kunden[sel_k_id].telefon if sel_k_id else "")
                m_val = cmob.text_input("Mobil", value=db.kunden[sel_k_id].mobil if sel_k_id else "")
                note = st.text_input("Notiz")
                
                if st.form_submit_button("Termin speichern"):
                    if sel_k_id:
                        kunde_obj = db.kunden[sel_k_id]  # Sichere Referenz aus der Datenbank
                        kunde_obj.telefon, kunde_obj.mobil = t_val, m_val
                        kunde_obj.termine.append(f"{d.strftime('%d.%m.%Y')} um {t.strftime('%H:%M')} - {note}")
                        speichern(db)
                        st.success("✅ Termin gebucht!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("⚠️ Bitte Kunden wählen!")


        with tab2:
            st.subheader("📋 Terminsuche") 
            if st.session_state.reset_overview_search:
                st.session_state.reset_overview_search = False; st.session_state.term_overview_search = ""; st.rerun()

            term_suche = st.text_input("Suche", key="term_overview_search")
            all_terms_list = []
            for k in db.kunden.values():
                for idx, t_str in enumerate(k.termine):
                    try:
                        p = t_str.split(" um "); d_dt = datetime.strptime(p[0], '%d.%m.%Y')
                        p2 = p[1].split(" - "); t_dt = datetime.strptime(p2[0], '%H:%M').time()
                        item = {"ID": k.kunden_id, "Anrede": k.anrede, "Vorname": k.vorname, "Nachname": k.nachname, "Wohnort": ", ".join(k.wohnorte), "PLZ": k.plz, "Telefon": k.telefon, "Mobil": k.mobil, "Datum": d_dt.strftime('%d.%m.%Y'), "Uhrzeit": t_dt.strftime('%H:%M'), "Notiz": p2[1] if len(p2)>1 else "", "idx": idx, "sort": datetime.combine(d_dt.date(), t_dt)}
                        
                        search_fields = [item['Vorname'], item['Nachname'], item['ID'], item['Wohnort'], item['PLZ'], item['Telefon'], item['Mobil']]
                        if not term_suche or any(term_suche.lower() in str(val).lower() for val in search_fields):
                            all_terms_list.append(item)
                    except: pass
            all_terms_list.sort(key=lambda x: x['sort'])

            if term_suche and all_terms_list:
                sel_item = st.selectbox("Auswahl zur Bearbeitung:", all_terms_list, index=None, placeholder="Termin wählen...", format_func=lambda x: f"{x['Nachname']}: {x['Datum']} {x['Uhrzeit']}", key="term_select_persist")
                if sel_item:
                    c_b1, c_b2 = st.columns(2)
                    if c_b1.button("✏️ Bearbeiten"):
                        st.session_state.edit_id = sel_item['ID']; st.session_state.edit_term_idx = sel_item['idx']; st.rerun()
                    if c_b2.button("❌ Schließen"):
                        st.session_state.edit_id = None; st.session_state.reset_overview_search = True; st.rerun()

            if st.session_state.edit_id and st.session_state.edit_term_idx is not None:
                curr_k = db.kunden.get(st.session_state.edit_id)
                if curr_k:
                    with st.form("edit_term_form"):
                        st.markdown(f"### ✏️ Termin bearbeiten: {curr_k.anrede} {curr_k.vorname} {curr_k.nachname}")
                        c1, c2 = st.columns(2)
                        new_d = c1.date_input("Datum", datetime.now()); new_t = c2.time_input("Uhrzeit", datetime.now().time())
                        ct2, cm2 = st.columns(2)
                        u_t = ct2.text_input("Telefon", curr_k.telefon); u_m = cm2.text_input("Mobil", curr_k.mobil)
                        new_n = st.text_input("Notiz")
                        b1, b2 = st.columns(2)
                        if b1.form_submit_button("💾 Speichern"):
                            curr_k.telefon, curr_k.mobil = u_t, u_m
                            curr_k.termine[st.session_state.edit_term_idx] = f"{new_d.strftime('%d.%m.%Y')} um {new_t.strftime('%H:%M')} - {new_n}"
                            speichern(db); st.success("✅ Gespeichert!"); time.sleep(3); st.rerun()
                        if b2.form_submit_button("🗑️ Löschen"):
                            st.session_state.delete_confirm = True; st.rerun()

                    if st.session_state.delete_confirm:
                        st.warning("⚠️ Möchten Sie diesen Termin wirklich löschen?")
                        dc1, dc2 = st.columns(2)
                        if dc1.button("✅ Ja, Termin löschen"):
                            curr_k.termine.pop(st.session_state.edit_term_idx); speichern(db); st.session_state.edit_id = None; st.session_state.delete_confirm = False; st.success("🗑️ Gelöscht!"); time.sleep(3); st.rerun()
                        if dc2.button("❌ Abbrechen"): st.session_state.delete_confirm = False; st.rerun()

            st.markdown("---")
            if all_terms_list:
                st.dataframe(pd.DataFrame(all_terms_list)[["ID", "Anrede", "Vorname", "Nachname", "Telefon", "Mobil", "Datum", "Uhrzeit", "Notiz"]], use_container_width=True, hide_index=True)

    # --- KUNDENSTAMM ---
    elif st.session_state.page == "Kundenstamm":
        st.title("📑 Kundenstamm")
        tab_k1, tab_k2 = st.tabs(["Kunde anlegen", "Kundensuche & Bearbeitung"])

        with tab_k1:
            st.subheader("Neuen Kunden erfassen")
            with st.form("add_kunde_stamm_new"):
                c1, c2 = st.columns(2)
                anr = c1.selectbox("Anrede *", ["", "Herr", "Frau", "Divers"], index=0)
                geschl = c2.selectbox("Geschlecht *", ["", "Männlich", "Weiblich", "Divers"], index=0)
                vname = c1.text_input("Vorname *")
                nname = c2.text_input("Nachname *")
                alt = c1.number_input("Alter", 1, 120, 1)
                mail = c2.text_input("E-Mail")
                plz = c1.text_input("Postleitzahl *")
                ort = c2.text_input("Wohnort *")
                tel = c1.text_input("Telefon * (nur Zahlen)")
                mob = c2.text_input("Mobil (nur Zahlen)")
                
                if st.form_submit_button("Kunden speichern"):
                    errors = []
                    if not anr: errors.append("Anrede fehlt.")
                    if not geschl: errors.append("Geschlecht fehlt.")
                    if not nname: errors.append("Nachname fehlt.")
                    if not vname: errors.append("Vorname fehlt.")
                    if not plz: errors.append("Postleitzahl fehlt.")
                    if not ort: errors.append("Wohnort fehlt.")
                    if not tel: errors.append("Telefon fehlt.")
                    if plz and not plz.isdigit(): errors.append("PLZ darf nur Zahlen enthalten.")
                    if tel and not tel.isdigit(): errors.append("Telefon darf nur Zahlen enthalten.")
                    if mob and mob.strip() and not mob.isdigit(): errors.append("Mobil darf nur Zahlen enthalten.")
                    if mail and mail.strip() and "@" not in mail: errors.append("Ungültige E-Mail Adresse (@ fehlt).")
                    
                    if errors:
                        st.error("⚠️ Folgende Fehler sind aufgetreten:\n\n* " + "\n* ".join(errors))
                    else:
                        neuer_k = Kunde(anr, vname, nname, geschl, alt, mail, [ort], plz=plz, telefon=tel, mobil=mob)
                        db.hinzufuegen(neuer_k); speichern(db)
                        st.success(f"✅ Kunde erfolgreich unter der ID {neuer_k.kunden_id} angelegt!"); time.sleep(3); st.rerun()

        with tab_k2:
            st.subheader("🔍 Kundensuche") 
            if st.session_state.reset_stamm_search:
                st.session_state.reset_stamm_search = False; st.session_state.stamm_suche = ""; st.rerun()

            suche = st.text_input("Suche", key="stamm_suche")
            display_kunden = []
            for k in db.kunden.values():
                search_data = [k.vorname, k.nachname, k.kunden_id, ", ".join(k.wohnorte), k.plz, k.telefon, k.mobil, k.email]
                if not suche or any(suche.lower() in str(v).lower() for v in search_data):
                    display_kunden.append(k)
            
            if suche and display_kunden:
                auswahl = st.selectbox("Kunde zur Bearbeitung:", display_kunden, index=None, placeholder="Bitte wählen...", format_func=lambda x: f"{x.nachname}, {x.vorname} ({x.kunden_id})", key="stamm_select_persist")
                if auswahl:
                    c_k_sel1, c_k_sel2 = st.columns(2)
                    if c_k_sel1.button("👤 Bearbeiten"):
                        st.session_state.edit_id = auswahl.kunden_id; st.rerun()
                    if c_k_sel2.button("❌ Schließen"):
                        st.session_state.edit_id = None; st.session_state.reset_stamm_search = True; st.rerun()
            
            if st.session_state.edit_id and st.session_state.edit_id in db.kunden:
                curr = db.kunden[st.session_state.edit_id]
                with st.form("edit_kunde_form"):
                    st.markdown(f"### ✏️ {curr.nachname} bearbeiten")
                    c1, c2 = st.columns(2)
                    u_anr = c1.selectbox("Anrede *", ["", "Herr", "Frau", "Divers"], index=["", "Herr", "Frau", "Divers"].index(curr.anrede) if curr.anrede in ["", "Herr", "Frau", "Divers"] else 0)
                    u_geschl = c2.selectbox("Geschlecht *", ["", "Männlich", "Weiblich", "Divers"], index=["", "Männlich", "Weiblich", "Divers"].index(curr.geschlecht) if curr.geschlecht in ["", "Männlich", "Weiblich", "Divers"] else 0)
                    u_vname = c1.text_input("Vorname *", curr.vorname); u_nname = c2.text_input("Nachname *", curr.nachname)
                    u_alt = c1.number_input("Alter", 1, 120, int(curr.alter) if str(curr.alter).isdigit() else 1)
                    u_mail = c2.text_input("E-Mail", curr.email)
                    u_plz = c1.text_input("Postleitzahl *", curr.plz); u_ort = c2.text_input("Wohnort *", ", ".join(curr.wohnorte))
                    u_tel = c1.text_input("Telefon * (nur Zahlen)", curr.telefon); u_mob = c2.text_input("Mobil (nur Zahlen)", curr.mobil)
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Änderungen speichern"):
                        e_edit = []
                        if not u_anr: e_edit.append("Anrede fehlt.")
                        if not u_geschl: e_edit.append("Geschlecht fehlt.")
                        if not u_nname: e_edit.append("Nachname fehlt.")
                        if not u_vname: e_edit.append("Vorname fehlt.")
                        if not u_plz: e_edit.append("Postleitzahl fehlt.")
                        if not u_ort: e_edit.append("Wohnort fehlt.")
                        if not u_tel: e_edit.append("Telefon fehlt.")
                        if u_plz and not u_plz.isdigit(): e_edit.append("PLZ darf nur Zahlen enthalten.")
                        if u_tel and not u_tel.isdigit(): e_edit.append("Telefon darf nur Zahlen enthalten.")
                        if u_mob and u_mob.strip() and not u_mob.isdigit(): e_edit.append("Mobil darf nur Zahlen enthalten.")
                        if u_mail and u_mail.strip() and "@" not in u_mail: e_edit.append("Ungültige E-Mail Adresse (@ fehlt).")
                        
                        if e_edit:
                            st.error("⚠️ Änderungen nicht gespeichert:\n\n* " + "\n* ".join(e_edit))
                        else:
                            db.bearbeiten(curr.kunden_id, anrede=u_anr, vorname=u_vname, nachname=u_nname, geschlecht=u_geschl, alter=u_alt, email=u_mail, wohnorte=[u_ort], plz=u_plz, telefon=u_tel, mobil=u_mob)
                            speichern(db); st.success("✅ Gespeichert!"); time.sleep(3); st.rerun()
                    if b2.form_submit_button("🗑️ Löschen"):
                        st.session_state.delete_confirm = True; st.rerun()
                
                if st.session_state.delete_confirm:
                    st.warning(f"⚠️ Möchten Sie den Kunden {curr.nachname} wirklich löschen?")
                    dk1, dk2 = st.columns(2)
                    if dk1.button("✅ Ja, Kunde löschen"):
                        db.loeschen(curr.kunden_id); speichern(db); st.session_state.edit_id = None; st.session_state.delete_confirm = False; st.success("🗑️ Gelöscht!"); time.sleep(3); st.rerun()
                    if dk2.button("❌ Abbrechen"): st.session_state.delete_confirm = False; st.rerun()

            st.markdown("---")
            if display_kunden:
                df_stamm = pd.DataFrame([k.to_table_row() for k in display_kunden])
                st.dataframe(df_stamm[["ID", "Anrede", "Vorname", "Nachname", "Geschlecht", "Alter", "Mobil", "Telefon", "E-Mail", "Termine vorhanden?"]], use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
