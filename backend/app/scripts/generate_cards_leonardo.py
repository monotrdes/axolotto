"""
generate_cards_leonardo.py
==========================
Genera las 54 cartas de la lotería Axolotto usando la API de Leonardo.ai.

Uso:
    export LEONARDO_API_KEY="tu_api_key"

    python -m app.scripts.generate_cards_leonardo \
        --reference-image /ruta/a/referencia.png \
        --output-dir ./output/cards

python backend/app/scripts/generate_cards_leonardo.py --reference-image backend/app/scripts/axolotto-image_reference.png --output-dir ./output/cards

python backend/app/scripts/generate_cards_leonardo.py --init-image-id 54aebf31-a871-4f30-8567-94e9f56eb609 --style-weight 0.2 --output-dir ./output/cards

NOTA: El webhook se configura globalmente en el API Manager de Leonardo.ai
      (https://app.leonardo.ai/settings/api-manager). No se pasa como argumento.

Opciones:
    --reference-image   Imagen de referencia de estilo (PNG/JPG)
    --output-dir        Directorio de salida (default: ./output/cards)
    --delay             Segundos de espera entre requests (default: 5)
    --model-id          ID del modelo Leonardo (default: Leonardo Diffusion XL)
    --init-image-id     Reusar un init_image_id previo (evita re-subir la referencia)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# 54 Cartas de la Lotería Axolotto
# ---------------------------------------------------------------------------
CARTAS_LOTERIA = {
    "01_el_axolotl": "a cute, highly expressive pink axolotl character standing in a cool and friendly waving pose, looking directly at the camera.",
    "02_el_diablito": "a cute, mischievously evil little red devil imp creature jumping mid-air in a chaotic frenzy, cackling wildly while swinging a tiny pitchfork that sparks with energy.",
    "03_la_jefa": "a proud, highly confident female jaguar character in a modern neon blazer, striding forward purposefully down a busy street while adjusting her glasses, looking away with a confident smirk.",
    "04_el_godin": "a frantic badger character furiously typing on an invisible keyboard while balancing a plastic lunch container on its lap, completely absorbed in stress.",
    "05_la_pinata": "a colorful traditional star-shaped piñata creature bursting open mid-air in a joyful explosion, scattering bright candies and paper confetti everywhere.",
    "06_la_tlanchana": "a mystical freshwater mermaid goddess swimming gracefully through an emerald current, her fish tail swirling aquatic plants into a glowing vortex.",
    "07_el_trompo": "a sentient vertical spit of pastor pork meat spinning furiously in a blur of motion, a thin trail of savory smoke rising from the pineapple on its head.",
    "08_la_botella": "a retro glass soda bottle character careening sideways as its metal cap pops off with an explosive, fizzy spray of bright red soda bubbles.",
    "09_el_molcajete": "a sturdy volcanic stone molcajete mortar creature energetically grinding vibrant red chiles with its pestle, splashing spicy salsa drops around.",
    "10_el_chilaquil": "a happy, chubby green chilaquil monster wrestling its way out from under a heavy, melting blanket of sour cream and cheese, throwing its arms up.",
    "11_el_aguacate": "a clumsy avocado character tripping over its own round brown seed, arms flailing wildly in a frantic but adorable tumble.",
    "12_el_luchador": "a muscular bulldog wrestler character diving mid-air off an invisible ring rope, paws tucked into a dramatic flying tackle gesture.",
    "13_el_sombrero": "a massive mariachi sombrero hat zooming horizontally through the frame like a UFO, its intricate embroidery glowing faintly.",
    "14_la_catrina": "an elegant skeleton lady character spinning gracefully in a heavy storm vortex of bright orange marigold petals, her dress rippling.",
    "15_el_maiz": "a cheerful ear of corn character bursting into a few popcorn kernels from its head due to intense excitement, green husks flaring out.",
    "16_la_bandera": "a proud, living tricolor flag character snapping violently in a heavy wind, its fabric twisting into dramatic, sharp ripple shapes.",
    "17_el_acordeon": "a lively musical accordion character squeezing its bellows intensely during a fast solo, musical notes physically bouncing off its keys.",
    "18_la_chancla": "a pink rubber sandal zooming through the air in a dizzying spiral loop, leaving sharp, dynamic comic-style speed lines behind it.",
    "19_el_firulais": "a scruffy stray mutt dog character chasing its own tail at high speed inside a chaotic dust cloud, barking with frantic energy.",
    "20_el_michi": "a grumpy orange tabby cat character mid-movement, swatting an invisible glass off the edge of a ledge with a cold, calculated paw swipe.",
    "21_el_chacmool": "a pre-Hispanic stone Chacmool character reclining on its side while balancing and spinning a giant fresh lime on its foot.",
    "22_los_tenis": "a pair of canvas sneakers sprinting so fast that their soles leave a trail of bright cartoon sparks, laces flying wildly behind.",
    "23_la_luna": "a glowing crescent moon character yawning deeply, pulling a thick star-patterned cloud over itself like a heavy winter blanket.",
    "24_el_colibri": "a tiny iridescent hummingbird character darting backwards at extreme speed, its flight captured in a sharp zig-zag motion pattern.",
    "25_la_caguama": "a giant brown glass bottle character tripping and tipping over backward, cold beer foam rushing out of its neck like a volcano eruption.",
    "26_el_cafe": "a classic pewter coffee pot character running frantically, hot dark coffee sloshing over its rim as it rushes to deliver a tray.",
    "27_el_corazon": "an anatomical red heart character sprinting hard like a marathon runner, sweating tiny cartoon drops while clutching a love letter.",
    "28_la_salsa": "a hot sauce bottle character spitting a literal stream of cartoon fire from its neck, rocket-propelling itself upwards due to extreme spice.",
    "29_el_chamoy": "a sticky red sauce monster melting into a gooey puddle while stretching its arms out frantically to catch a falling mango slice.",
    "30_el_aguachile": "a group of cured shrimp characters with funny eyes aggressively surfing on a massive, curling wave of bright green lime juice.",
    "31_el_papel_picado": "a sheet of bright orange perforated paper twisting and turning gracefully as it floats down through a sudden gust of wind.",
    "32_el_musico": "an avant-garde creature inspired by Juan Son, headbanging wildly on stage so its feather costume flies outward, screaming into a broken microphone.",
    "33_la_arana": "a fluffy black spider character weaving a complex web at hyper-speed, its eight tiny legs a complete blur of motion.",
    "34_el_alebrije": "a magnificent fantasy creature leaping between invisible floating rocks, leaving a trail of neon stardust behind its jaguar paws.",
    "35_la_estrella": "a bright golden star character sliding down a steep rainbow trail like a skateboarder, leaving a wake of shimmering cosmic dust.",
    "36_el_pan": "a sweet pink concha sweet bread character diving headfirst into a giant bowl of hot chocolate, splashing thick brown foam everywhere.",
    "37_el_tlacuache": "a heroic little opossum scrambling up a dark tree branch, tightly clutching a brilliant, crackling ember of stolen fire in its bare paws.",
    "38_el_taco": "a crispy taco character skidding to a halt on a slippery surface, its meat and cilantro filling throwing slightly forward from the momentum.",
    "39_el_nopal": "a cute cactus pad character accidentally hugging a floating balloon, looking mortified as the balloon pops with a 'POW' visual effect.",
    "40_el_alacran": "a small purple scorpion character scuttling sideways in a frantic panic, trying to dodge a giant falling drop of rain.",
    "41_la_rosa": "a beautiful red rose character plucking its own thorns and throwing them like darts while leaning forward in a dramatic fencing pose.",
    "42_la_calavera": "a decorated sugar skull character laughing hysterically, its jaw completely detached and floating slightly below the skull in a funny way.",
    "43_la_campana": "a heavy golden church bell character vibrating violently mid-swing, visible sound waves blasting out and cracking the air around it.",
    "44_el_cantarito": "an orange clay cantarito cup character shaking violently like a cocktail shaker, splashing mezcal and salt grains into the air.",
    "45_el_cacomixtle": "a cute cacomixtle character stealing a pastry from an invisible shelf, leaping away into the dark with its long ringed tail in mid-air.",
    "46_el_sol": "a massive radiant sun character mid-sneeze, accidentally blasting a powerful, chaotic solar flare across the upper sky.",
    "47_el_penacho": "a floating Aztec feather headdress spinning in a grand ceremonial dance, its long green quetzal feathers creating a swirling emerald vortex.",
    "48_la_chalupa": "a small wooden canoe boat character rowing furiously down a canal, wooden oars splashing water as colorful flowers bounce around.",
    "49_el_vocho": "a chubby retro Beetle car character drifting wildly around a sharp corner on two wheels, thick white smoke billowing from its tires.",
    "50_el_pescado": "a prehistoric pejelagarto alligator gar fish wrestling with a fishing line, twisting its long toothy body into a fierce knot of resistance.",
    "51_la_cobija": "a cozy animal character rolling down a steep grassy hill like a giant burrito, completely wrapped up inside its heavy tiger blanket.",
    "52_la_maceta": "a terracotta clay pot character sprouting a massive vine at hyper-speed that shoots straight up, lifting the pot off the ground like a rocket.",
    "53_el_elote": "a street corn character slipping on a stray pat of butter, spinning like an ice skater while cheese flakes fly off like snow.",
    "54_la_botarga": "a goofy character in a puffy white doctor suit doing an energetic breakdance move on the street, its costume inflating hilariously.",
}

# ---------------------------------------------------------------------------
# Template de estilo maestro (mismo que generate_card_images.py)
# ---------------------------------------------------------------------------
def construir_prompt(descripcion_personaje: str) -> str:
    return f"""Full-body portrait of {descripcion_personaje}

[Art Style]: The style is a raw, unique vintage trading card illustration, meticulously blending the cozy whimsical aesthetic of "Hilda", the bold stylized character geometry of "The Amazing World of Gumball", and the raw indie comic book feel of "Adventure Time". Completely avoid generic digital vector, smooth gradients, or corporate commercial clip-art looks.

[Visual Elements]: Feature highly expressive hand-drawn, artisanal details with a slightly messy but professional execution. Expect organic, slightly rough bold ink outlines with natural hand tremors, flat screen-printed color fills with grit, visible heavy ink bleed, and a distinct raw cardstock paper grain texture over the character's body. Authentic risograph printing flaws.

[Composition]: Vertical alignment, character captured mid-action, completely ignoring the camera and fully immersed in its own activity. Completely isolated on a solid flat pure white background. No floor, no shadows, no text, no borders."""


# ---------------------------------------------------------------------------
# Cliente Leonardo.ai
# ---------------------------------------------------------------------------
LEONARDO_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
# Phoenix 1.0 — el mejor modelo de Leonardo para ilustración/arte (2024/2025)
DEFAULT_MODEL_ID = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"


def get_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def upload_reference_image(api_key: str, image_path: str) -> str:
    """
    Sube la imagen de referencia a Leonardo.ai mediante el flujo presigned S3.
    Devuelve el init_image_id para reutilizar en todas las generaciones.
    """
    path = Path(image_path)
    if not path.exists():
        print(f"❌ Imagen de referencia no encontrada: {image_path}")
        sys.exit(1)

    extension = path.suffix.lstrip(".").lower()
    if extension not in ("png", "jpg", "jpeg", "webp"):
        print(f"❌ Extensión no soportada: {extension}. Usa PNG, JPG o WEBP.")
        sys.exit(1)
    # Leonardo acepta "jpg" no "jpeg"
    ext_for_api = "jpg" if extension == "jpeg" else extension

    print(f"📤 Subiendo imagen de referencia: {path.name}")

    with httpx.Client(timeout=60) as client:
        # Paso 1: Pedir presigned URL
        resp = client.post(
            f"{LEONARDO_BASE_URL}/init-image",
            headers=get_headers(api_key),
            json={"extension": ext_for_api},
        )
        if resp.status_code != 200:
            print(f"❌ Error al obtener presigned URL: {resp.status_code} — {resp.text}")
            sys.exit(1)

        data = resp.json()
        upload_info = data.get("uploadInitImage", {})
        image_id = upload_info.get("id")
        s3_url = upload_info.get("url")
        s3_fields_raw = upload_info.get("fields", {})

        if not image_id or not s3_url:
            print(f"❌ Respuesta inesperada de /init-image: {data}")
            sys.exit(1)

        # Leonardo devuelve 'fields' como string JSON serializado — hay que parsearlo
        if isinstance(s3_fields_raw, str):
            try:
                s3_fields: dict = json.loads(s3_fields_raw)
            except json.JSONDecodeError:
                print(f"❌ No se pudo parsear 'fields' de S3: {s3_fields_raw[:200]}")
                sys.exit(1)
        else:
            s3_fields = s3_fields_raw

        print(f"   🔑 init_image_id: {image_id}")

        # Paso 2: Subir el archivo a S3 con el presigned URL
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Los fields del presigned URL van como form-data, la imagen al FINAL (S3 lo requiere así)
        form_fields = {k: (None, v) for k, v in s3_fields.items()}
        form_fields["file"] = (path.name, image_bytes)

        # El upload a S3 NO lleva el header Authorization de Leonardo
        s3_resp = client.post(s3_url, files=form_fields)
        if s3_resp.status_code not in (200, 204):
            print(f"❌ Error al subir a S3: {s3_resp.status_code} — {s3_resp.text[:200]}")
            sys.exit(1)

        print(f"   ✅ Imagen de referencia subida correctamente.")
        return image_id


def submit_generation(
    api_key: str,
    card_name: str,
    prompt: str,
    style_image_id: str,
    model_id: str,
    image_prompt_weight: float = 0.3,
    num_images: int = 2,
) -> str:
    """
    Envía una petición de generación a Leonardo.ai y devuelve el generationId.

    Usa `imagePrompts` (referencia de estilo puro) en lugar de `init_image_id`
    (img2img que morfea la imagen base). Así el prompt manda y la referencia
    solo aporta el estilo visual sin alterar la composición.

    El webhook se configura globalmente en el API Manager de Leonardo.ai.
    """
    payload = {
        "modelId": model_id,
        "prompt": prompt,
        # 2:3 vertical — trading card format
        "width": 832,
        "height": 1248,
        "num_images": num_images,
        # Imagen de referencia usada SOLO como guía de estilo (no img2img)
        "imagePrompts": [style_image_id],
        "imagePromptWeight": image_prompt_weight,
        # Calidad máxima con Phoenix
        "alchemy": True,
        "contrast": 3.5,          # Contraste medio-alto para ilustración con detalle
        "guidance_scale": 7,      # Adherencia al prompt (7 = recomendado por Leonardo)
        "num_inference_steps": 40, # Más pasos = más calidad (default es 15)
        "presetStyle": "ILLUSTRATION",
        "enhancePrompt": False,   # Nuestros prompts son suficientemente detallados
        # Negative prompt para mantener el estilo limpio
        "negative_prompt": (
            "photo, realistic, 3d render, photograph, watermark, text, signature, "
            "border, frame, complex background, gradient background, blurry, "
            "low quality, ugly, deformed, duplicate"
        ),
    }

    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{LEONARDO_BASE_URL}/generations",
            headers=get_headers(api_key),
            json=payload,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    generation_id = data.get("sdGenerationJob", {}).get("generationId")
    if not generation_id:
        raise RuntimeError(f"No se encontró generationId en la respuesta: {data}")

    return generation_id


def load_mapping(mapping_path: Path) -> dict:
    if mapping_path.exists():
        with open(mapping_path) as f:
            return json.load(f)
    return {}


def save_mapping(mapping_path: Path, mapping: dict):
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Genera las 54 cartas de lotería con Leonardo.ai + webhook."
    )
    parser.add_argument(
        "--reference-image",
        required=False,
        help="Ruta a la imagen de referencia de estilo (PNG/JPG)",
    )
    parser.add_argument(
        "--output-dir",
        default="./output/cards",
        help="Directorio donde se guardarán las imágenes (default: ./output/cards)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Segundos de espera entre requests para respetar rate limits (default: 5)",
    )
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="ID del modelo Leonardo.ai (default: Phoenix 1.0)",
    )
    parser.add_argument(
        "--init-image-id",
        default=None,
        help="Reusar un init_image_id previo como estilo (evita re-subir la imagen de referencia)",
    )
    parser.add_argument(
        "--num-images",
        type=int,
        default=2,
        help="Variantes a generar por carta (default: 2)",
    )
    parser.add_argument(
        "--style-weight",
        type=float,
        default=0.3,
        help="Peso de la imagen de estilo: 0=ignorar, 1=seguir al máximo (default: 0.3)",
    )

    args = parser.parse_args()

    # Leer API key
    api_key = os.environ.get("LEONARDO_API_KEY")
    if not api_key:
        print("❌ Falta la variable de entorno LEONARDO_API_KEY")
        print("   Exporta con: export LEONARDO_API_KEY='tu_api_key'")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    mapping_path = output_dir / "jobs_mapping.json"

    # -------------------------------------------------------------------
    # Obtener init_image_id
    # -------------------------------------------------------------------
    if args.init_image_id:
        init_image_id = args.init_image_id
        print(f"♻️  Reusando init_image_id previo: {init_image_id}")
    elif args.reference_image:
        init_image_id = upload_reference_image(api_key, args.reference_image)
        print(f"\n💾 Guarda este ID para reusar sin re-subir la imagen:")
        print(f"   --init-image-id {init_image_id}\n")
    else:
        print("❌ Debes pasar --reference-image o --init-image-id")
        sys.exit(1)

    # -------------------------------------------------------------------
    # Cargar mapping existente (para reanudar sesión)
    # -------------------------------------------------------------------
    mapping = load_mapping(mapping_path)
    reverse_mapping = {v: k for k, v in mapping.items()}  # card_name → gen_id

    print(f"\n🃏 Total de cartas: {len(CARTAS_LOTERIA)}")
    print(f"📁 Directorio de salida: {output_dir.resolve()}")
    print(f"🤖 Modelo: {args.model_id}")
    print(f"⏱️  Delay entre requests: {args.delay}s\n")

    submitted = 0
    skipped = 0

    for card_name, descripcion in CARTAS_LOTERIA.items():
        card_dir = output_dir / card_name

        # Skip si ya tiene las imágenes descargadas
        if card_dir.exists() and len(list(card_dir.glob("variante_*.png"))) >= args.num_images:
            print(f"⏩ {card_name} ya tiene {args.num_images} variantes. Saltando...")
            skipped += 1
            continue

        # Skip si ya fue enviada a Leonardo (esperando webhook)
        if card_name in reverse_mapping:
            gen_id = reverse_mapping[card_name]
            print(f"⏳ {card_name} ya enviada (gen: {gen_id[:8]}...). Esperando webhook...")
            skipped += 1
            continue

        # Construir prompt completo
        prompt = construir_prompt(descripcion)

        print(f"🚀 Enviando: {card_name}...")

        try:
            generation_id = submit_generation(
                api_key=api_key,
                card_name=card_name,
                prompt=prompt,
                style_image_id=init_image_id,
                model_id=args.model_id,
                image_prompt_weight=args.style_weight,
                num_images=args.num_images,
            )

            # Guardar en el mapping
            mapping[generation_id] = card_name
            save_mapping(mapping_path, mapping)
            reverse_mapping[card_name] = generation_id

            print(f"   ✅ gen_id: {generation_id[:8]}... → guardado en jobs_mapping.json")
            submitted += 1

        except Exception as e:
            print(f"   ❌ Error en {card_name}: {e}")
            print("🛑 Proceso pausado. Revisa tu API key o cuota.")
            break

        # Rate limiting
        if submitted < len(CARTAS_LOTERIA):
            print(f"   💤 Esperando {args.delay}s...")
            time.sleep(args.delay)

    print(f"\n{'='*50}")
    print(f"📊 Resumen:")
    print(f"   ✅ Enviadas: {submitted}")
    print(f"   ⏩ Saltadas: {skipped}")
    print(f"   📄 Mapping guardado en: {mapping_path.resolve()}")
    print(f"\n⌛ Ahora espera los webhooks de Leonardo.ai.")
    print(f"   Las imágenes se guardarán en: {output_dir.resolve()}/{{card_name}}/")


if __name__ == "__main__":
    main()
