import os
import time
from google import genai
from google.genai import types

# Recuerda exportar tu API key en la terminal: export GEMINI_API_KEY="xxx"
# 1. Inicializar el cliente oficial de Google GenAI (Forzando la versión estable v1)
client = genai.Client(api_key="AIzaSyBfku1CpuLkZUob_mXAhNF9x8Kj_qgJ_R8")

# 2. El mazo de 54 cartas con dinamismo puro (Viviendo en su universo)
cartas_loteria = {
    #"01_el_axolotl": "a cute, highly expressive pink axolotl character standing in a cool and friendly waving pose, looking directly at the camera.",
    #"02_el_diablito": "a cute, mischievously evil little red devil imp creature jumping mid-air in a chaotic frenzy, cackling wildly while swinging a tiny pitchfork that sparks with energy.",
    #"03_la_jefa": "a proud, highly confident female jaguar character in a modern neon blazer, striding forward purposefully down a busy street while adjusting her glasses, looking away with a confident smirk.",
    #"04_el_godin": "a frantic badger character furiously typing on an invisible keyboard while balancing a plastic lunch container on its lap, completely absorbed in stress.",
    #"05_la_pinata": "a colorful traditional star-shaped piñata creature bursting open mid-air in a joyful explosion, scattering bright candies and paper confetti everywhere.",
    #"06_la_tlanchana": "a mystical freshwater mermaid goddess swimming gracefully through an emerald current, her fish tail swirling aquatic plants into a glowing vortex.",
    #"07_el_trompo": "a sentient vertical spit of pastor pork meat spinning furiously in a blur of motion, a thin trail of savory smoke rising from the pineapple on its head.",
    #"08_la_botella": "a retro glass soda bottle character careening sideways as its metal cap pops off with an explosive, fizzy spray of bright red soda bubbles.",
    #"09_el_molcajete": "a sturdy volcanic stone molcajete mortar creature energetically grinding vibrant red chiles with its pestle, splashing spicy salsa drops around.",
    #"10_el_chilaquil": "a happy, chubby green chilaquil monster wrestling its way out from under a heavy, melting blanket of sour cream and cheese, throwing its arms up.",
    #"11_el_aguacate": "a clumsy avocado character tripping over its own round brown seed, arms flailing wildly in a frantic but adorable tumble.",
    #"12_el_luchador": "a muscular bulldog wrestler character diving mid-air off an invisible ring rope, paws tucked into a dramatic flying tackle gesture.",
    #"13_el_sombrero": "a massive mariachi sombrero hat zooming horizontally through the frame like a UFO, its intricate embroidery glowing faintly.",
    #"14_la_catrina": "an elegant skeleton lady character spinning gracefully in a heavy storm vortex of bright orange marigold petals, her dress rippling.",
    #"15_el_maiz": "a cheerful ear of corn character bursting into a few popcorn kernels from its head due to intense excitement, green husks flaring out.",
    #"16_la_bandera": "a proud, living tricolor flag character snapping violently in a heavy wind, its fabric twisting into dramatic, sharp ripple shapes.",
    #"17_el_acordeon": "a lively musical accordion character squeezing its bellows intensely during a fast solo, musical notes physically bouncing off its keys.",
    #"18_la_chancla": "a pink rubber sandal zooming through the air in a dizzying spiral loop, leaving sharp, dynamic comic-style speed lines behind it.",
    #"19_el_firulais": "a scruffy stray mutt dog character chasing its own tail at high speed inside a chaotic dust cloud, barking with frantic energy.",
    #"20_el_michi": "a grumpy orange tabby cat character mid-movement, swatting an invisible glass off the edge of a ledge with a cold, calculated paw swipe.",
    #"21_el_chacmool": "a pre-Hispanic stone Chacmool character reclining on its side while balancing and spinning a giant fresh lime on its foot.",
    #"22_los_tenis": "a pair of canvas sneakers sprinting so fast that their soles leave a trail of bright cartoon sparks, laces flying wildly behind.",
    #"23_la_luna": "a glowing crescent moon character yawning deeply, pulling a thick star-patterned cloud over itself like a heavy winter blanket.",
    #"24_el_colibri": "a tiny iridescent hummingbird character darting backwards at extreme speed, its flight captured in a sharp zig-zag motion pattern.",
    #"25_la_caguama": "a giant brown glass bottle character tripping and tipping over backward, cold beer foam rushing out of its neck like a volcano eruption.",
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
    "54_la_botarga": "a goofy character in a puffy white doctor suit doing an energetic breakdance move on the street, its costume inflating hilariously."
}

# 3. La plantilla maestra "Messy pero Pro" de Imagen 4.0
def construir_prompt(descripcion_personaje):
    return f"""Full-body portrait of {descripcion_personaje}
    
[Art Style]: The style is a raw, unique vintage trading card illustration, meticulously blending the cozy whimsical aesthetic of "Hilda", the bold stylized character geometry of "The Amazing World of Gumball", and the raw indie comic book feel of "Adventure Time". Completely avoid generic digital vector, smooth gradients, or corporate commercial clip-art looks.

[Visual Elements]: Feature highly expressive hand-drawn, artisanal details with a slightly messy but professional execution. Expect organic, slightly rough bold ink outlines with natural hand tremors, flat screen-printed color fills with grit, visible heavy ink bleed, and a distinct raw cardstock paper grain texture over the character's body. Authentic risograph printing flaws.

[Composition]: Vertical alignment, character captured mid-action, completely ignoring the camera and fully immersed in its own activity. Completely isolated on a solid flat pure white background. No floor, no shadows, no text, no borders."""

# 4. Motor de generación en lote (Estabilizado para 2 variantes)
def generar_baraja():
    os.makedirs("output", exist_ok=True)
    
    for nombre_carta, descripcion in cartas_loteria.items():
        output_dir = f"output/{nombre_carta}"
        
        # FIX: Ahora salta si ya existen al menos 2 variantes en la carpeta
        if os.path.exists(output_dir) and len(os.listdir(output_dir)) >= 2:
            print(f"⏩ {nombre_carta} ya generada con sus variantes. Saltando...")
            continue
            
        print(f"🚀 Generando lote para: {nombre_carta}...")
        os.makedirs(output_dir, exist_ok=True)
        
        prompt_final = construir_prompt(descripcion)
        
        try:
            # Petición optimizada a 2 imágenes por lote
            result = client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt_final,
                config=types.GenerateImagesConfig(
                    number_of_images=2,
                    aspect_ratio="3:4",
                    output_mime_type="image/png",
                    person_generation="DONT_ALLOW"
                )
            )
            
            # Guardar las variantes individuales
            for index, generated_image in enumerate(result.generated_images):
                file_path = f"{output_dir}/variante_{index + 1}.png"
                with open(file_path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
                print(f"  ✅ Variante {index + 1}/2 guardada.")
                
            # FIX: 30 segundos de enfriamiento para blindar la cuota de la API
            print("💤 Esperando 30 segundos para enfriar la API...")
            time.sleep(30)
            
        except Exception as e:
            print(f"  ❌ Error crítico en {nombre_carta}: {e}")
            print("🛑 Proceso pausado. Revisa tus credenciales o cuota de API.")
            break

if __name__ == "__main__":
    generar_baraja()