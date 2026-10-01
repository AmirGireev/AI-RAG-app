import os
import ssl
import urllib.request

# create data folder
os.makedirs("data", exist_ok=True)

ssl_context = ssl._create_unverified_context()

pdf_sources = {
    # Spain MITECO
    "es_lince_estrategia_2024.pdf": "https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/publicaciones/estrategias/Estrategia-lince-24-07-24.pdf",
    "es_lobo_medidas.pdf": "https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/conservacion-de-especies-amenazadas/LOBO_tcm30-195185.pdf",
    "es_oso_pardo_protocolo.pdf": "https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/conservacion-de-especies/protocolointervencionososcantabricos_aprobadocepnb_tcm30-527062.pdf",
    "es_lince_boletin_2024.pdf": "https://www.miteco.gob.es/content/dam/miteco/es/parques-nacionales-oapn/centros-fincas/lince/boletines-lince/Boletin_Linces_OAPN_2024_2semestre_DEFINITIVO3.pdf",

    # PORTUGAL ICNF
    "pt_encnb_biodiversidade_2030.pdf": "https://www.icnf.pt/api/file/doc/42bf20badeb783ab",
    "pt_lobo_iberico_censo.pdf": "https://www.icnf.pt/api/file/doc/3db73b1336574f6a",
    "pt_aguia_imperial_guia.pdf": "https://www.icnf.pt/api/file/doc/21e183260b741ba4",
    "pt_lince_icnf_ficha.pdf": "https://www.icnf.pt/api/file/doc/7056e2874281ba9b",
    
    # EU
    "eu_lynx_release_protocol_en.pdf": "https://lifelynxconnect.eu/wp-content/uploads/2022/09/Releases-protocol.pdf",
    "eu_lynx_stepping_stones_en.pdf": "https://lifelynxconnect.eu/wp-content/uploads/2022/09/Stepping-stone-selection-protocol.pdf",
    "eu_lynx_conservation_status_en.pdf": "https://lifelynxconnect.eu/wp-content/uploads/2022/02/2012_Reverse_decline_Simon.pdf",
    "eu_wildlife_in_spain.pdf": "https://wildanimalsineurope.home.blog/wp-content/uploads/2019/02/wild-animals-in-spain.pdf",
    "eu_asturias_wildlife_guide.pdf": "https://sa80ca0103d5397d0.jimcontent.com/download/version/1661966319/module/8174993464/name/Ecotourism%20in%20Asturias%20%28ENG%29.pdf"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for filename, url in pdf_sources.items():
    filepath = os.path.join("data", filename)
    

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context) as response, open(filepath, "wb") as f:
            f.write(response.read())
    except Exception as e:
        print(f"error downloading {filename}: {e}")

print("\nsuccessfully downloaded all PDFs!")