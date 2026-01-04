#!/bin/bash

# Arrête le script à la moindre erreur
set -e

# 🧠 CALCUL AUTOMATIQUE DES CHEMINS
# On demande à Python où sont installés cuBLAS et cuDNN et on l'ajoute au chemin système.
export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`:$LD_LIBRARY_PATH

echo "🔧 [Entrypoint] Configuration GPU chargée pour CUDA 12.4."
echo "📂 [Entrypoint] LD_LIBRARY_PATH mis à jour."

# 🚀 LANCEMENT DE LA COMMANDE
# "exec $@" signifie : "Exécute la commande qu'on m'a donnée ensuite"
# Dans ton cas, ce sera : uvicorn main:app --host 0.0.0.0 --port 8000 --reload
exec "$@"