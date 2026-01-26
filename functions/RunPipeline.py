from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score  # ← ADICIONE!
import mne, pandas as pd, importlib.util, os
from typing import Optional
import numpy as np
import json

class RunPipeline:
    """Executa pipeline ML em dados EEG"""
    
    def __init__(self):
        self.pipeline = None
    
    def load_pipeline(self, json_path: str) -> bool:
        """Carrega JSON → scikit-learn Pipeline"""
        try:
            with open(json_path, 'r') as f:
                dados = json.load(f)
            
            etapas = []
            for etapa in dados["etapas"]:
                nome_plugin = etapa["plugin"]
                params = etapa.get("parametros", {})
                params = {k.replace(" ", "_").replace("º", "o"): v for k, v in params.items()}
                
                caminho = os.path.join("functions", "plugins", nome_plugin, "method.py")
                spec = importlib.util.spec_from_file_location("PluginMethod", caminho)
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)
                
                classe = getattr(modulo, "PluginMethod")
                instancia = classe(**params)
                etapas.append((nome_plugin, instancia))
            
            self.pipeline = Pipeline(etapas)
            return True
        except Exception as e:
            print(f"Erro load_pipeline: {e}")
            return False
    
    def load_eeg_data(self, csv_path: str, duration: float = 5.0) -> Optional[mne.io.Raw]:
        """CSV → MNE Raw com events"""
        df = pd.read_csv(csv_path)
        eventos = df[['timestamp', 'events']].loc[df['events'] != 0]
        dados_eeg = df.drop(columns=['timestamp', 'events'])
        
        channel_names = dados_eeg.columns.tolist()  # ← FIX AQUI!
        array_dados = dados_eeg.to_numpy()
        
        info = mne.create_info(ch_names=channel_names, sfreq=250, ch_types='eeg')
        raw = mne.io.RawArray(array_dados.T, info)
        
        for tempo, tipo in eventos.values:
            if tipo == 11:  # MI1
                raw.annotations.append(tempo, duration, 'MI1')
            else:  # MI2
                raw.annotations.append(tempo, duration * 3, 'MI2')
        
        return raw
    
    def execute(self, csv_path: str) -> dict:
        """Executa pipeline completo → métricas"""
        raw = self.load_eeg_data(csv_path)
        if not raw or not self.pipeline:
            return {"error": "Dados ou pipeline inválido"}
        
        # Pré-processamento padrão MI
        montage = mne.channels.make_standard_montage("standard_1005")
        raw.set_montage(montage).filter(8.0, 25.0)
        
        events, event_id = mne.events_from_annotations(raw)  # ← Detecta AUTO!
        print(f"Eventos detectados: {event_id}")  # Debug
        picks = mne.pick_types(raw.info, eeg=True)
        epochs = mne.Epochs(raw, events, event_id, 
                           tmin=-1, tmax=4, preload=True,
                           event_repeated='drop')
        
        epochs_train = epochs.crop(tmin=1, tmax=2)
        X = epochs_train.get_data()
        y = epochs_train.events[:, -1]
        
        cv_scores = cross_val_score(self.pipeline, X, y, cv=5, n_jobs=-1)
        score = cv_scores.mean()
        
        self.pipeline.fit(X, y)  # Fit final
        
        return {
            "accuracy": round(score * 100, 2),
            "cv_scores": [round(s*100, 1) for s in cv_scores],
            "n_epochs": len(epochs),
            "event_id": str(event_id),
            "n_classes": len(np.unique(y))
        }
