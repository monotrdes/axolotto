from google import genai

# Usa tu llave (¡la nueva que generes después de borrar la expuesta!)
client = genai.Client(api_key="AIzaSyBfku1CpuLkZUob_mXAhNF9x8Kj_qgJ_R8")

print("🔍 Buscando modelos de Imagen disponibles para tu cuenta:")
try:
    for model in client.models.list():
        if 'imagen' in model.name.lower():
            print(f"  ⭐ {model.name}")
except Exception as e:
    print(f"❌ Error al listar: {e}")