# PyPulse

Contrôle d'instruments pour expériences de physique quantique.

## Instruments supportés
- **PulseStreamer 8/2** (Swabian Instruments) — générateur de séquences d'impulsions
- **Carte NI DAQ** — acquisition de données
- **Keysight RF** — source RF

## Structure du projet
```
PyPulse/
├── hardware/          # Drivers bas niveau pour chaque instrument
├── sequences/         # Définition des séquences de mesure (Rabi, T1, T2…)
├── config/            # Fichiers de configuration (YAML)
├── gui/               # Interface graphique PyQt5
├── utils/             # Fonctions utilitaires
├── tests/             # Tests unitaires
├── data/              # Données de mesure (ignoré par git)
├── main.py            # Point d'entrée principal
└── requirements.txt   # Dépendances Python
```

## Installation
```bash
pip install -r requirements.txt
```

## Lancement
```bash
python main.py
```
